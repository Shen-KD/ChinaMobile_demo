import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { AppState, Theme, Conversation, Message } from '../types'
import { DEFAULT_MODEL, BACKEND_API_CONFIG } from '../config'

const generateId = () => Math.random().toString(36).substring(2, 15)

// Global variable to track ticket validation status
let validatingTicket: string | null = null;

const generateTitle = (firstMessage: string): string => {
  const maxLength = 20
  const cleaned = firstMessage.replace(/\n/g, ' ').trim()
  if (cleaned.length <= maxLength) return cleaned
  return cleaned.substring(0, maxLength) + '...'
}

export const useStore = create<AppState>()(
  persist(
    (set, get) => ({
      theme: 'dark' as Theme,
      sidebarCollapsed: false,
      conversations: [],
      currentConversationId: null,
      isLoading: false,
      isRedirecting: false,
      isValidating: false,
      selectedModel: DEFAULT_MODEL,
      user: null,

      checkAuth: async () => {
        const baseUrl = BACKEND_API_CONFIG.baseUrl || '';
        try {
          // 1. Check if there is a ticket in the URL
          const urlParams = new URLSearchParams(window.location.search);
          const ticket = urlParams.get('ticket');
          
          if (ticket) {
             // If we are already validating THIS ticket, stop here
             if (validatingTicket === ticket) {
                 return;
             }
             validatingTicket = ticket;
             set({ isValidating: true });

             // Validate ticket
             const serviceUrl = window.location.origin + window.location.pathname; // Remove query params
             
             try {
                const response = await fetch(`${baseUrl}/api/auth/validate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ticket, service: serviceUrl })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.user) {
                        set({ user: data.user, isValidating: false });
                        // Clear ticket from URL
                        window.history.replaceState({}, document.title, window.location.pathname);
                        validatingTicket = null;
                        return;
                    }
                }
             } catch (e) {
                 console.error("Ticket validation failed", e);
             } finally {
                // Wait a bit before clearing to ensure no race conditions with double-invocations in StrictMode
                // Or just clear it if we are done. 
                // Actually, if it failed, we might want to let it try again if the user reloads, but for now reset it.
                // However, in StrictMode, the second call happens almost immediately. 
                // We keep it set until we redirect or finish.
                if (validatingTicket === ticket) {
                    setTimeout(() => { validatingTicket = null; }, 1000);
                }
                // Ensure validating state is cleared even if failed
                set({ isValidating: false });
             }
             // If validation failed, continue to check existing session or redirect to login
          }

          // 2. Check existing session
          const response = await fetch(`${baseUrl}/api/auth/user`);
          if (response.ok) {
            const data = await response.json();
            if (data.success && data.user) {
              set({ user: data.user });
            } else {
              set({ user: null, isRedirecting: true });
              // Not logged in, redirect to CAS login via backend
              const service = window.location.origin + window.location.pathname;
              window.location.href = `${baseUrl}/api/auth/login?service=${encodeURIComponent(service)}`;
            }
          } else {
            set({ user: null, isRedirecting: true });
            // Not logged in, redirect to CAS login via backend
            const service = window.location.origin + window.location.pathname;
            window.location.href = `${baseUrl}/api/auth/login?service=${encodeURIComponent(service)}`;
          }
        } catch (e) {
          set({ user: null, isRedirecting: true });
          // Network error or other issue
           const service = window.location.origin + window.location.pathname;
           window.location.href = `${baseUrl}/api/auth/login?service=${encodeURIComponent(service)}`;
        }
      },

      logout: () => {
        set({ user: null, isRedirecting: true });
        const baseUrl = BACKEND_API_CONFIG.baseUrl || '';
        const service = window.location.origin;
        window.location.href = `${baseUrl}/api/auth/logout?service=${encodeURIComponent(service)}`;
      },

      toggleTheme: () => {
        set((state) => ({
          theme: state.theme === 'dark' ? 'light' : 'dark'
        }))
      },

      initTheme: () => {
        const stored = localStorage.getItem('sourcing-agent-storage')
        if (stored) {
          const parsed = JSON.parse(stored)
          if (parsed.state?.theme) return
        }
        
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        set({ theme: prefersDark ? 'dark' : 'light' })
      },

      toggleSidebar: () => {
        set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed
        }))
      },

      createConversation: () => {
        const newConversation: Conversation = {
          id: generateId(),
          title: '新对话',
          messages: [],
          createdAt: Date.now(),
          updatedAt: Date.now()
        }
        
        set((state) => ({
          conversations: [newConversation, ...state.conversations],
          currentConversationId: newConversation.id
        }))
      },

      selectConversation: (id: string) => {
        set({ currentConversationId: id })
      },

      deleteConversation: (id: string) => {
        set((state) => {
          const filtered = state.conversations.filter(c => c.id !== id)
          const newCurrentId = state.currentConversationId === id
            ? (filtered[0]?.id || null)
            : state.currentConversationId
          
          return {
            conversations: filtered,
            currentConversationId: newCurrentId
          }
        })
      },

      renameConversation: (id: string, newTitle: string) => {
        set((state) => ({
          conversations: state.conversations.map(conv =>
            conv.id === id
              ? { ...conv, title: newTitle, updatedAt: Date.now() }
              : conv
          )
        }))
      },

      addMessage: (messageData) => {
        const { currentConversationId, createConversation } = get()
        
        let targetConversationId = currentConversationId
        
        if (!targetConversationId) {
          createConversation()
          targetConversationId = get().currentConversationId
        }
        
        const newMessage: Message = {
          ...messageData,
          id: generateId(),
          timestamp: Date.now()
        }
        
        set((state) => ({
          conversations: state.conversations.map(conv => {
            if (conv.id !== targetConversationId) return conv
            
            const updatedMessages = [...conv.messages, newMessage]
            const isFirstUserMessage = messageData.role === 'user' && conv.messages.length === 0
            
            return {
              ...conv,
              messages: updatedMessages,
              title: isFirstUserMessage ? generateTitle(messageData.content) : conv.title,
              updatedAt: Date.now()
            }
          })
        }))
        
        return newMessage.id
      },

      updateMessage: (messageId: string, updates: Partial<Message>) => {
        set((state) => ({
          conversations: state.conversations.map(conv => ({
            ...conv,
            messages: conv.messages.map(msg =>
              msg.id === messageId ? { ...msg, ...updates } : msg
            )
          }))
        }))
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      getCurrentConversation: () => {
        const { conversations, currentConversationId } = get()
        return conversations.find(c => c.id === currentConversationId) || null
      },

      setSelectedModel: (modelId: string) => {
        set({ selectedModel: modelId })
      }
    }),
    {
      name: 'sourcing-agent-storage',
      partialize: (state) => ({
        theme: state.theme,
        conversations: state.conversations,
        currentConversationId: state.currentConversationId,
        selectedModel: state.selectedModel,
        user: state.user
      })
    }
  )
)
