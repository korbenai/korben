"""arXiv API library functions."""

import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict

logger = logging.getLogger(__name__)

# Atom namespace
ATOM_NS = '{http://www.w3.org/2005/Atom}'
ARXIV_NS = '{http://arxiv.org/schemas/atom}'


def search_papers(
    query: str,
    max_results: int = 10,
    start: int = 0,
    sort_by: str = 'relevance',
    sort_order: str = 'descending'
) -> Dict:
    """
    Search for academic papers using the arXiv API.
    
    Args:
        query: Search query string (e.g., 'all:electron' or 'ti:transformer')
        max_results: Maximum number of results to return (default: 10)
        start: Starting index for pagination (default: 0)
        sort_by: Sort by 'relevance', 'lastUpdatedDate', or 'submittedDate' (default: 'relevance')
        sort_order: 'ascending' or 'descending' (default: 'descending')
        
    Returns:
        dict: Dictionary containing search results
        
    Raises:
        RuntimeError: If API request fails
    """
    base_url = 'http://export.arxiv.org/api/query'
    
    # Build query parameters
    params = {
        'search_query': query,
        'start': start,
        'max_results': max_results,
        'sortBy': sort_by,
        'sortOrder': sort_order
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    logger.info(f"Searching arXiv for: {query}")
    
    try:
        response = urllib.request.urlopen(url)
        xml_data = response.read().decode('utf-8')
        
        # Parse the XML response
        papers = _parse_arxiv_response(xml_data)
        
        logger.info(f"Found {len(papers)} papers")
        
        return {
            'papers': papers,
            'total_results': len(papers),
            'query': query,
            'start': start,
            'max_results': max_results
        }
        
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP error occurred: {e.code}"
        logger.error(f"{error_msg}\n{e.reason}")
        raise RuntimeError(f"{error_msg}: {e.reason}")
    except urllib.error.URLError as e:
        error_msg = f"URL error occurred: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def _parse_arxiv_response(xml_data: str) -> List[Dict]:
    """
    Parse arXiv Atom XML response into a list of paper dictionaries.
    
    Args:
        xml_data: XML string from arXiv API
        
    Returns:
        List of paper dictionaries
    """
    papers = []
    
    try:
        root = ET.fromstring(xml_data)
        
        # Find all entry elements
        for entry in root.findall(f'{ATOM_NS}entry'):
            paper = {}
            
            # Title
            title_elem = entry.find(f'{ATOM_NS}title')
            if title_elem is not None:
                paper['title'] = title_elem.text.strip().replace('\n', ' ')
            
            # Summary/Abstract
            summary_elem = entry.find(f'{ATOM_NS}summary')
            if summary_elem is not None:
                paper['abstract'] = summary_elem.text.strip().replace('\n', ' ')
            
            # Authors
            authors = []
            for author in entry.findall(f'{ATOM_NS}author'):
                name_elem = author.find(f'{ATOM_NS}name')
                if name_elem is not None:
                    authors.append(name_elem.text)
            paper['authors'] = authors
            
            # ID (arXiv ID)
            id_elem = entry.find(f'{ATOM_NS}id')
            if id_elem is not None:
                paper['id'] = id_elem.text
                paper['url'] = id_elem.text
            
            # Published date
            published_elem = entry.find(f'{ATOM_NS}published')
            if published_elem is not None:
                paper['published'] = published_elem.text
            
            # Updated date
            updated_elem = entry.find(f'{ATOM_NS}updated')
            if updated_elem is not None:
                paper['updated'] = updated_elem.text
            
            # PDF link
            for link in entry.findall(f'{ATOM_NS}link'):
                if link.get('title') == 'pdf':
                    paper['pdf_url'] = link.get('href')
                elif link.get('rel') == 'alternate':
                    paper['html_url'] = link.get('href')
            
            # Primary category
            primary_cat = entry.find(f'{ARXIV_NS}primary_category')
            if primary_cat is not None:
                paper['primary_category'] = primary_cat.get('term')
            
            # All categories
            categories = []
            for cat in entry.findall(f'{ATOM_NS}category'):
                term = cat.get('term')
                if term:
                    categories.append(term)
            paper['categories'] = categories
            
            # Comment
            comment_elem = entry.find(f'{ARXIV_NS}comment')
            if comment_elem is not None:
                paper['comment'] = comment_elem.text
            
            # Journal reference
            journal_elem = entry.find(f'{ARXIV_NS}journal_ref')
            if journal_elem is not None:
                paper['journal_ref'] = journal_elem.text
            
            # DOI
            doi_elem = entry.find(f'{ARXIV_NS}doi')
            if doi_elem is not None:
                paper['doi'] = doi_elem.text
            
            papers.append(paper)
        
        return papers
        
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML response: {e}")
        raise RuntimeError(f"Failed to parse XML response: {e}")



