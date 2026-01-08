import { useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import { useStore } from './store'
import { BACKEND_API_CONFIG } from './config'
import './styles/App.css'

function App() {
  const { theme, initTheme, checkAuth, isRedirecting, isValidating } = useStore()

  useEffect(() => {
    initTheme()
    checkAuth()
  }, [initTheme, checkAuth])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  if (isRedirecting) {
    const baseUrl = BACKEND_API_CONFIG.baseUrl || '';
    const service = window.location.origin + window.location.pathname;
    const loginUrl = `${baseUrl}/api/auth/login?service=${encodeURIComponent(service)}`;

    return (
      <div className="redirect-loading" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        gap: '20px'
      }}>
        <div className="loading-spinner" style={{
          width: '40px',
          height: '40px',
          border: '3px solid var(--border-color)',
          borderTopColor: 'var(--accent-primary)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{ fontSize: '16px', fontWeight: 500 }}>正在跳转至统一认证平台...</p>
        <a 
          href={loginUrl} 
          style={{ 
            marginTop: '10px', 
            color: 'var(--accent-primary)', 
            textDecoration: 'none',
            fontSize: '14px' 
          }}
        >
          如果未自动跳转，请点击此处
        </a>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }

  if (isValidating) {
    return (
      <div className="redirect-loading" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        gap: '20px'
      }}>
        <div className="loading-spinner" style={{
          width: '40px',
          height: '40px',
          border: '3px solid var(--border-color)',
          borderTopColor: 'var(--accent-primary)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{ fontSize: '16px', fontWeight: 500 }}>正在验证登录信息...</p>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    )
  }

  return (
    <div className="app">
      <Sidebar />
      <ChatArea />
    </div>
  )
}

export default App
