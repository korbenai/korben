"""Google Calendar API client for retrieving calendar events.

This module provides a service class for interacting with Google Calendar API
using service account credentials with domain-based credential lookup.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Google Calendar API client with domain-based credential lookup.
    
    Credentials are looked up in the following order:
    1. Domain-specific: ~/.google/credentials/{domain}/credentials.json
    2. Email-specific: ~/.google/credentials/{email}/credentials.json
    3. Default: ~/.google/credentials/credentials.json
    """
    
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    
    def __init__(self, email: str):
        """Initialize Google Calendar service for a specific email.
        
        Args:
            email: Email address to access calendar for
            
        Raises:
            ValueError: If email format is invalid
            FileNotFoundError: If credentials file not found
        """
        self.email = email
        self.service_account_file = self._find_credentials_for_domain(email)
        self.service = self._build_service()
    
    def _find_credentials_for_domain(self, email: str) -> str:
        """Extract domain from email and find credentials file.
        
        Args:
            email: Email address to extract domain from
            
        Returns:
            Path to credentials file
            
        Raises:
            ValueError: If email format is invalid
            FileNotFoundError: If credentials file not found
        """
        if '@' not in email:
            raise ValueError("Invalid email address format")
        
        domain = email.split('@')[1]
        home = Path.home()
        
        # Try domain-specific credentials first
        domain_creds = home / '.google' / 'credentials' / domain / 'credentials.json'
        if domain_creds.exists():
            logger.info(f"Using credentials for domain {domain}: {domain_creds}")
            return str(domain_creds)
        
        # Fallback to email-specific credentials
        email_creds = home / '.google' / 'credentials' / email / 'credentials.json'
        if email_creds.exists():
            logger.info(f"Using credentials for email {email}: {email_creds}")
            return str(email_creds)
        
        # Fallback to default credentials
        default_creds = home / '.google' / 'credentials' / 'credentials.json'
        if default_creds.exists():
            logger.info(f"Using default credentials: {default_creds}")
            return str(default_creds)
        
        raise FileNotFoundError(
            f"No credentials found for domain {domain} or email {email}. "
            f"Expected one of: {domain_creds}, {email_creds}, {default_creds}"
        )
    
    def _build_service(self):
        """Build and return Google Calendar API service.
        
        Returns:
            Google Calendar API service instance
        """
        creds = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.SCOPES
        )
        return build("calendar", "v3", credentials=creds)
    
    def get_events_by_date(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Get calendar events for a specific date range.
        
        Args:
            start_date: Start date/time (defaults to today at midnight UTC)
            end_date: End date/time (defaults to end of start day)
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries containing event details
        """
        # Default to today if no dates provided
        if start_date is None:
            now = datetime.now(timezone.utc)
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date is None:
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Ensure timezone-aware datetimes
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
        
        time_min = start_date.isoformat()
        time_max = end_date.isoformat()
        
        logger.info(f"Fetching events for {self.email} from {time_min} to {time_max}")
        
        try:
            events_result = self.service.events().list(
                calendarId=self.email,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                maxResults=max_results,
            ).execute()
            
            events = events_result.get("items", [])
            logger.info(f"Found {len(events)} events for {self.email}")
            
            # Format events for easier consumption
            formatted_events = []
            for event in events:
                formatted_event = self._format_event(event)
                formatted_events.append(formatted_event)
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error fetching events for {self.email}: {e}")
            raise
    
    def _format_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format a raw calendar event into a cleaner structure.
        
        Args:
            event: Raw event from Google Calendar API
            
        Returns:
            Formatted event dictionary
        """
        start = event["start"].get("dateTime") or event["start"].get("date")
        end = event["end"].get("dateTime") or event["end"].get("date")
        
        # Determine if all-day event
        is_all_day = "T" not in start
        
        # Format times for display
        if is_all_day:
            start_formatted = start
            end_formatted = end
        else:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            start_formatted = start_dt.strftime("%Y-%m-%d %H:%M")
            end_formatted = end_dt.strftime("%Y-%m-%d %H:%M")
        
        return {
            "id": event.get("id"),
            "title": event.get("summary", "<no title>"),
            "description": event.get("description", ""),
            "location": event.get("location", ""),
            "start": start_formatted,
            "end": end_formatted,
            "start_raw": start,
            "end_raw": end,
            "is_all_day": is_all_day,
            "attendees": event.get("attendees", []),
            "organizer": event.get("organizer", {}),
            "status": event.get("status", ""),
            "html_link": event.get("htmlLink", ""),
        }

