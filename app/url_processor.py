from app.config import settings
import re
import os

# ------------------------------------------------------------------------------------------------
# Startup Tasks
# ------------------------------------------------------------------------------------------------
firecrawl = None

def load_firecrawl():
    global firecrawl
    from firecrawl import Firecrawl
    firecrawl = Firecrawl(api_key=settings.firecrawl_api_key)

def ensure_temp_folder():
    if not os.path.exists(settings.temp_dir):
        os.mkdir(settings.temp_dir)

# ------------------------------------------------------------------------------------------------
# Validating URL
# ------------------------------------------------------------------------------------------------
def is_valid_url(url) -> bool:
    """Checks whether the link is a valid http or https url or not"""
    https_pattern = r"https:\/\/(www\.)?.*(\.).*\/"
    http_pattern = r"http:\/\/(www\.)?.*(\.).*\/"

    is_valid_url = re.match(https_pattern, url) or re.match(http_pattern, url)

    return is_valid_url

# ------------------------------------------------------------------------------------------------
# Scraping Sitemap
# ------------------------------------------------------------------------------------------------
async def scrape_sitemap(url):
    """Scrapes the sitemap of the given url using firecrawl's map endpoint"""
    map = firecrawl.map(url)
    links = [link.url for link in map.links]
    links = {link.replace("www.", "") for link in links}
    return links

# ------------------------------------------------------------------------------------------------
# Scraping Pages & Saving 
# ------------------------------------------------------------------------------------------------
async def scrape_links(url, domain, links):
    """Scrapes each page's content and saves it as a markdown file"""

    path = f"{settings.temp_dir}/{domain}"
    if not os.path.exists(path):
        os.mkdir(path) # Creating a new folder inside the temp folder so we can delete that whole folder when the user wants to delete a website's content

    idx = 0
    for link in links:
        try:
            page_path = link.replace(url[:-1], "") # /home, /contact-us
            file_name = f"{idx}{page_path if page_path else "-root"}.md" # https://seorank.pk/home --> 0/home.md, https://seorank.pk/ --> 0-root.md
            file_name = file_name.replace("/", "-") # 0/home.md --> 0-home.md
            file_path = f"{settings.temp_dir}/{domain}/{file_name}" # ./uploads/hussamkazim.com/0-home.md
            md_content = firecrawl.scrape(link, formats=["markdown"]).markdown # getting the markdown from the firecrawl scrape result object
            
            with open(file_path, "w") as file: # Saving the scraped data to a md file
                file.write(md_content)

            idx += 1

        except Exception as e: # Skipping page if firecrawl is unable to scrape it. e.g. sitemap.xml
            print(f"skipping {link}.")

