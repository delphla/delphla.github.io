const puppeteer = require('puppeteer');
const fs = require('fs');
const { promisify } = require('util');

// Function to download images
async function downloadImage(url, filename) {
    const response = await page.goto(url, { waitUntil: 'networkidle2' });
    await promisify(fs.writeFile)(filename, await response.buffer());
}

// Function to save as markdown
async function saveAsMarkdown(title, content, date_published, category, image_urls) {
    const page_dir = `posts/${title}`;
    await promisify(fs.mkdir)(page_dir, { recursive: true });

    // Replace image urls in content
    image_urls.forEach((image_url, i) => {
        const local_image_path = `/img/${title}/image_${i}.jpg`;
        content = content.replace(image_url, local_image_path);
    });

    // Write to markdown file
    await promisify(fs.writeFile)(`${page_dir}.md`, `---\ntitle: "${title}"\ndate: ${date_published}\ncategory: "${category}"\n---\n\n${content}`);
}

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Wait for manual login
    await page.goto('https://blog.sina.com.cn/s/blog_1581b7b9b0102z7ve.html');
    await page.waitForTimeout(20000); // Adjust time for manual login

    // Loop through blog posts
    while (true) {
        // Download post
        const title = await page.title();
        const category = await page.$eval('.blog_class a', el => el.textContent);
        const date_published = await page.$eval('.time', el => el.textContent);
        const content = await page.$eval('.articalContent', el => el.outerHTML);

        const image_urls = await page.evaluate(() => {
            const images = Array.from(document.querySelectorAll('img'));
            return images.map(img => img.src);
        });

        await saveAsMarkdown(title, content, date_published, category, image_urls);

        // Navigate to previous blog post
        const prev_button = await page.$('.articalfrontback > div:first-child a');
        if (prev_button) {
            await prev_button.click();
            await page.waitForTimeout(2000); // Adjust wait time as needed
        } else {
            break;
        }
    }

    await browser.close();
})();
