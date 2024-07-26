import requests
from bs4 import BeautifulSoup
import sys
import re

def get_linkedin_url_from_domain(domain):
    domain = domain.replace('http://', '').replace('https://', '')
    url = f"http://{domain}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the domain: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    linkedin_url = None

    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'linkedin.com/company' in href or 'linkedin.com/in' in href:
            linkedin_url = href
            break

    if linkedin_url:
        print(f"LinkedIn URL found on the domain: {linkedin_url}")
        return linkedin_url
    else:
        print("LinkedIn URL not found on the domain.")
        return None

def clean_url(url):
    return re.sub(r'\?.*$', '', url).strip()

def verify_company_name_on_linkedin(linkedin_url, company_name):
    try:
        response = requests.get(linkedin_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error verifying the LinkedIn URL: {e}")
        return False, None

    soup = BeautifulSoup(response.text, 'html.parser')
    company_name_element = soup.find('h1', class_='org-top-card-summary__title')
    if company_name_element:
        page_name = company_name_element.get_text(strip=True)
        return page_name.lower() == company_name.lower(), page_name
    else:
        print("Company name not found on the LinkedIn page.")
        return False, None

def get_linkedin_url(company_name, company_domain=None):
    linkedin_url = None
    if company_domain:
        linkedin_url_from_domain = get_linkedin_url_from_domain(company_domain)
        if linkedin_url_from_domain:
            linkedin_url = linkedin_url_from_domain

    search_query = f"{company_name} site:linkedin.com"
    google_search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(google_search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error performing Google search: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a')

    linkedin_urls = []
    for result in results:
        href = result.get('href')
        if href and 'linkedin.com/company' in href:
            url = href.split('&')[0].replace('/url?q=', '')
            linkedin_urls.append(clean_url(url))

    if not linkedin_urls:
        print(f"No LinkedIn URLs found for {company_name}.")
        return None

    if linkedin_url:
        linkedin_url = clean_url(linkedin_url)
        for url in linkedin_urls:
            if clean_url(url).lower() == linkedin_url.lower():
                is_match, verified_name = verify_company_name_on_linkedin(url, company_name)
                if is_match:
                    print(f"Verified LinkedIn URL: {url}")
                    return url
                else:
                    print(f"LinkedIn URL mismatch: {linkedin_urls[0]} != {linkedin_url} (Verified name: {verified_name})")
                    return None

    print(f"Found LinkedIn URL: {linkedin_urls[0]}")
    return linkedin_urls[0]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <company_name> [company_domain]")
        sys.exit(1)

    company_name = sys.argv[1]
    company_domain = sys.argv[2] if len(sys.argv) > 2 else None

    linkedin_url = get_linkedin_url(company_name, company_domain)
    if linkedin_url:
        print(f"LinkedIn URL for {company_name}: {linkedin_url}")
    else:
        print(f"Failed to find LinkedIn URL for {company_name}.")
