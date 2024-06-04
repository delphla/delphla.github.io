from selenium import webdriver
import os
import time
from selenium.webdriver.common.by import By
from markdownify import markdownify as md
from bs4 import BeautifulSoup

driver = webdriver.Firefox()

# Save to markdown
def save_as_markdown(title, content, date_published, category, image_urls,image_elements):
    # Define the file name using date_published and title
    file_name = f"{date_published.split()[0]}_{title}"

    # Check if the markdown file already exists
    if os.path.exists(os.path.join('posts', f"{file_name}.md")):
        print(f"Markdown file already exists: {file_name}.md. Skipping...")
        return

    # Create page path 
    page_path = os.path.join('posts', file_name)

    # Replace image URLs with github paths# Replace image URLs with github paths
    for i, image_url in enumerate(image_urls):
        image_dir = os.path.join('static', 'img', file_name)
        local_image_path = f"../{image_dir}/image_{i}.png"
        os.makedirs(image_dir, exist_ok=True) # Create img directory
        # Open the image URL in a new tab
        driver.execute_script(f"window.open('{image_url}', '_blank');")
        time.sleep(4)  # Wait for the new tab to open
        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])
        # Take a screenshot
        driver.save_screenshot(os.path.join(image_dir, f'image_{i}.png'))
        # Close the new tab
        driver.close()
        # Switch back to the original tab
        driver.switch_to.window(driver.window_handles[0])

    # Replace image elements in the content
    for i, image_element in enumerate(image_elements):
        content = content.replace(image_element, f"![{title}]https://github.com/delphla/delphla.github.io/blob/main/{local_image_path}")

    # Write to markdown file
    with open(page_path + '.md', 'w') as f:
        f.write(f"---\n")
        f.write(f"title: {title}\n")  # Remove quotation marks
        f.write(f"date: {date_published}\n")  # Remove parentheses
        f.write(f"category: {category}\n")  # Remove quotation marks
        f.write(f"---\n\n")
        content = md(content)
        f.write(content)

    print(f"Markdown file saved: {file_name}.md")

driver.get("https://passport.weibo.com/sso/signin?entry=homepage&source=sinafloatlayer&url=https://blog.sina.com.cn/s/blog_1581b7b9b0102z7ve.html")


# Wait for login
input("login manually and press enter to continue")
os.makedirs("posts", exist_ok=True)  # Create posts directory if it doesn't exist

# Link to most recent post
driver.get("https://blog.sina.com.cn/s/blog_1581b7b9b0102z7ve.html")

# Loop through blog posts
while True:
    # Download post
    title_element = driver.find_element(By.CLASS_NAME, "titName")
    title = title_element.text.strip()
    try:
        category_element = driver.find_element(By.CSS_SELECTOR, ".blog_class a")
        category = category_element.text if category_element else "Uncategorized"
    except:
        category = "Uncategorized"
    date_published = driver.find_element(By.CSS_SELECTOR, ".time").text.strip('()')  # Remove parentheses
   

    # Define the file name using date_published and title
    file_name = f"{date_published.split()[0]}_{title}"

    # Check if the markdown file already exists
    if os.path.exists(os.path.join('posts', f"{file_name}.md")):
        print(f"Markdown file already exists: {file_name}.md. Skipping...")
    else:
        content = driver.find_element(By.CSS_SELECTOR, ".articalContent").get_attribute("outerHTML")
        image_urls = [a['href'] for a in BeautifulSoup(content, 'html.parser').find_all('a', href=True) if a.find('img')]
        image_elements = [str(a) for a in BeautifulSoup(content, 'html.parser').find_all('a', href=True) if a.find('img')]

        save_as_markdown(title, content, date_published, category, image_urls,image_elements)

    # Navigate to prev post
    prev_button = driver.find_element(By.CSS_SELECTOR, ".articalfrontback > div:first-child a")
    if prev_button:
        prev_button.click()
        time.sleep(2)
    else:
        break
