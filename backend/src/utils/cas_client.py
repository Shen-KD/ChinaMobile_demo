import urllib.parse
import httpx
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, Tuple
import logging

from src.config import settings

logger = logging.getLogger(__name__)

class CASClient:
    def __init__(self, cas_server_url: str, app_base_url: str):
        self.cas_server_url = cas_server_url.rstrip('/')
        self.app_base_url = app_base_url.rstrip('/')

    def get_login_url(self, service_url: str) -> str:
        """
        Construct the CAS login URL with the service parameter.
        """
        params = {'service': service_url}
        if settings.MODE == 'test':
            params['redirect'] = 'forbid'
        return f"{self.cas_server_url}/login?{urllib.parse.urlencode(params)}"

    def get_logout_url(self, service_url: Optional[str] = None) -> str:
        """
        Construct the CAS logout URL.
        """
        url = f"{self.cas_server_url}/logout"
        if service_url:
            params = {'service': service_url}
            if settings.MODE == 'test':
                params['redirect'] = 'forbid'
            url += f"?{urllib.parse.urlencode(params)}"
        return url

    async def validate_ticket(self, ticket: str, service_url: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate the ticket with the CAS server.
        Returns: (is_valid, username, attributes)
        """
        validate_url = f"{self.cas_server_url}/serviceValidate"
        params = {
            'ticket': ticket,
            'service': service_url
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(validate_url, params=params, timeout=10.0)
                response.raise_for_status()
                content = response.text
                logger.debug(f"CAS Validation Response: {content}")
                
                return self._parse_cas_response(content)
        except Exception as e:
            logger.error(f"CAS validation failed: {str(e)}")
            return False, None, {}

    def _parse_cas_response(self, xml_content: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Parse the XML response from CAS.
        """
        try:
            # Handle namespaces usually present in CAS responses
            # CAS 2.0 often uses http://www.yale.edu/tp/cas
            namespaces = {'cas': 'http://www.yale.edu/tp/cas'}
            
            # Remove namespace prefixes for easier parsing if needed, but using proper NS is better
            # However, sometimes ElementTree with namespaces is tricky if they change.
            # A robust way is to ignore namespace or handle both.
            
            root = ET.fromstring(xml_content)
            
            # Check for success
            # We try to find 'authenticationSuccess' in any namespace
            success_node = None
            for child in root:
                if child.tag.endswith('authenticationSuccess'):
                    success_node = child
                    break
            
            if success_node is not None:
                # Extract user
                user_node = None
                for child in success_node:
                    if child.tag.endswith('user'):
                        user_node = child
                        break
                
                username = user_node.text if user_node is not None else None
                
                # Extract attributes if present
                attributes = {}
                # Sometimes attributes are direct children of authenticationSuccess, sometimes in <cas:attributes>
                # Let's look for an attributes node
                attr_node = None
                for child in success_node:
                    if child.tag.endswith('attributes'):
                        attr_node = child
                        break
                
                if attr_node is not None:
                    for attr in attr_node:
                        # tag might be {ns}name, we want just name
                        key = attr.tag.split('}')[-1] if '}' in attr.tag else attr.tag
                        attributes[key] = attr.text
                
                return True, username, attributes
            
            else:
                # Check for failure to log it
                failure_node = None
                for child in root:
                    if child.tag.endswith('authenticationFailure'):
                        failure_node = child
                        break
                if failure_node is not None:
                    logger.warning(f"CAS Ticket Validation Failed: {failure_node.text}")
                
                return False, None, {}

        except ET.ParseError as e:
            logger.error(f"XML Parse Error: {e}")
            return False, None, {}

cas_client = CASClient(settings.CAS_SERVER_URL, settings.APP_BASE_URL)

