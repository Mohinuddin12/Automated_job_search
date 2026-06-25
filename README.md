# Automated Job Search Dashboard

A powerful automation tool that monitors multiple job portal websites daily and displays matching job opportunities in a modern, clean dashboard. Share jobs directly to WhatsApp with a single click!

## 🎯 Features

- **Multi-Website Monitoring**: Track jobs across 10+ company career pages simultaneously
- **Smart Job Filtering**: Uses intelligent regex patterns to identify relevant positions (DevOps, Network Engineers, QA Engineers, etc.)
- **Beautiful Dashboard**: Modern, responsive HTML report with card-based design
- **One-Click WhatsApp Sharing**: Share individual job postings directly to WhatsApp
- **GitHub Actions Integration**: Runs automatically or manually - no local PC needed
- **Fresh Data Daily**: Gets latest job listings every run - no data storage
- **Mobile Friendly**: Responsive design works perfectly on phones and tablets

## 🚀 Quick Start

### Prerequisites

- GitHub account (free)
- Python 3.10+ (for local testing)
- `requests` and `beautifulsoup4` libraries

### Installation

1. **Clone or Create Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Automated_job_search.git
   cd Automated_job_search
   ```

2. **Install Dependencies** (for local testing)
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Your Job Keywords** (Optional)
   Edit `automation.py` and customize:
   ```python
   SEARCH_URLS = [
       "https://yourcompany.com/careers",
       # Add more URLs
   ]
   
   JOB_TITLE_PATTERNS = [
       r"\byour job title\b",
       # Add more patterns
   ]
   
   WHATSAPP_PHONE_NUMBER = "+880XXXXX"  # Your WhatsApp number
   ```

## 📖 How to Use

### Option 1: GitHub Actions (Recommended - No Local Setup)

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/your-repo-name.git
   git push -u origin main
   ```

2. **Run Workflow Manually**
   - Go to your GitHub repository
   - Click **Actions** tab
   - Select **Daily Job Check** workflow
   - Click **Run workflow** button
   - Wait for completion (2-3 minutes)

3. **View Results**
   - Check the generated `index.html` in your repo
   - Click "Share on WhatsApp" to send individual jobs

### Option 2: Local Testing

```bash
# Run once
python automation.py

# View the generated index.html in your browser
```

## 📋 Configuration Guide

### Edit Target Websites

In `automation.py`, update `SEARCH_URLS`:

```python
SEARCH_URLS = [
    "https://genexinfosys.com/position.php",
    "https://brainstation-23.com/careers",
    "https://yourcompany.com/jobs",
    # Add or remove URLs as needed
]
```

### Add/Remove Job Titles

Update `JOB_TITLE_PATTERNS`:

```python
JOB_TITLE_PATTERNS = [
    r"\bdevops engineer\b",
    r"\bcloud engineer\b",
    r"\byour job title\b",
    # Use \b for word boundaries
]
```

### Set WhatsApp Number

In `automation.py`, update:

```python
WHATSAPP_PHONE_NUMBER = "+8801785210338"  # Format: country code + number
```

## 🔧 Understanding the Code

### Main Components

- **`fetch_page(url)`**: Downloads HTML from a website
- **`extract_job_posts(html, url)`**: Finds job titles from HTML (searches links and headings)
- **`is_job_link(text, href)`**: Checks if text/URL matches job keywords
- **`build_html_report(jobs)`**: Creates beautiful HTML dashboard
- **`build_whatsapp_url(message)`**: Generates WhatsApp share link

### How It Works

1. Fetches HTML from each configured website
2. Searches for text matching job title patterns
3. Also searches for job context keywords (career, vacancy, jobs, etc.)
4. Extracts matching jobs from both links and heading tags
5. Removes duplicates
6. Generates beautiful HTML report with WhatsApp buttons
7. **NO data storage** - fresh check every time

## 📊 Output

The script generates `index.html` with:

- **Header**: Shows total jobs found
- **Job Cards**: Each job displays:
  - Job title (clickable to job listing)
  - Company/Source page
  - When job was found
  - "View Job" button (opens job page)
  - "Share on WhatsApp" button (sends only that job)

## 🔄 Scheduling

### GitHub Actions Automation (Free)

The workflow currently runs **manually only**. To enable automatic daily runs:

Edit `.github/workflows/daily-job-check.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
    - cron: '0 14 * * 1,3,5'  # Mon, Wed, Fri at 2 PM UTC
  workflow_dispatch:
```

Save and push to enable automated scheduling.

### Windows Task Scheduler (Local PC)

1. Create `run_job_check.bat`:
   ```batch
   cd "e:\New python project"
   .\.venv\Scripts\python.exe automation.py
   ```

2. Open Task Scheduler
3. Create Basic Task → Trigger: Daily → Action: Run above batch file

## 💾 Storage & Privacy

- **NO job history stored** - script runs fresh every time
- **NO personal data** - only job titles and URLs
- **Stored files**: Only `index.html` (the report)
- **GitHub storage**: Free public repos get unlimited Actions minutes

## 🤖 Free GitHub Actions Credits

- **Public repo**: Unlimited free minutes ✅
- **Private repo**: 2000 free minutes/month (plenty!)
- Each run = ~5-10 minutes of usage

To get unlimited credits: Make repo **public** or upgrade to GitHub Pro ($4/month).

## ❓ Troubleshooting

### No Jobs Found?

1. Check if websites are accessible: `requests.get(url)`
2. Verify job title patterns match actual text on pages
3. Some websites block automation - try different ones

### WhatsApp Button Not Working?

- Ensure WhatsApp is installed on your device
- Check `WHATSAPP_PHONE_NUMBER` format (+country-code)
- Try opening WhatsApp link directly in browser first

### GitHub Actions Failed?

- Check **Actions** tab for error logs
- Ensure `requirements.txt` exists
- Verify Python code syntax (run locally first)

## 📝 Example: Adding a New Website

1. Find career page URL: `https://example.com/careers`
2. Add to `SEARCH_URLS`:
   ```python
   SEARCH_URLS = [
       ...existing urls...,
       "https://example.com/careers",
   ]
   ```
3. Run workflow to test
4. If no jobs found, the site might need custom patterns or blocking automation

## 🛠️ Customization Ideas

- Change HTML colors/fonts in `build_html_report()`
- Add email notifications
- Filter jobs by location/salary
- Add job descriptions extraction
- Create dashboard with job statistics

## 📄 License

This project is open source and free to use.

## 🙋 Support

If you have questions or encounter issues:

1. Check this README first
2. Review the automation.py comments
3. Test locally before running on GitHub
4. Check GitHub Actions logs for errors

---

**Happy Job Hunting! 🎉**

Built with ❤️ for automated job searching
