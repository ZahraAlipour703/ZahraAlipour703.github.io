# Ali Torabi - Personal Website

A modern, professional personal website showcasing research, projects, and experience in Computer Vision and Deep Learning.

## 🌟 Features

- **Responsive Design**: Fully responsive across all devices
- **Modern UI/UX**: Clean, professional design with smooth animations
- **Fast Loading**: Optimized performance and lazy loading
- **SEO Optimized**: Meta tags and semantic HTML
- **Interactive**: Smooth scrolling, hover effects, and animations
- **GitHub Pages Ready**: Easy deployment to GitHub Pages

## 🚀 Live Demo

Once deployed, your website will be live at:
```
https://selfishout.github.io
```

## 📁 Structure

```
personal-website/
├── index.html              # Main HTML file
├── assets/
│   ├── css/
│   │   └── style.css      # Styles and animations
│   ├── js/
│   │   └── script.js      # Interactive features
│   └── images/
│       └── profile.jpg    # Your profile photo
└── README.md              # This file
```

## 🎨 Customization

### Update Your Information

1. **LinkedIn & Social Media Links**
   - Edit line 53-62 in `index.html`
   - Replace placeholder URLs with your actual profiles

2. **Google Scholar**
   - Add your Google Scholar profile URL (line 58)

3. **Publications**
   - Update publication links in the Publications section
   - Add DOI or actual URLs to your papers

4. **Projects**
   - All 12 projects are already linked to your GitHub repos
   - Update project images if you have screenshots

### Update Colors (Optional)

Edit the CSS variables in `assets/css/style.css` (lines 10-20):

```css
:root {
    --primary-color: #667eea;     /* Main brand color */
    --secondary-color: #764abc;    /* Secondary brand color */
    --accent-color: #f59e0b;      /* Accent color */
}
```

## 📦 Deployment to GitHub Pages

### Method 1: Create New Repository (Recommended)

1. **Create a new repository named exactly: `selfishout.github.io`**
   ```
   Go to: https://github.com/new
   Repository name: selfishout.github.io
   Description: Personal Website
   Public: Yes
   Don't initialize with README
   ```

2. **Navigate to your website folder**
   ```bash
   cd "/Users/alitorabi/Documents/Projects/pythonProject/GitHub Portfolio Projects/personal-website"
   ```

3. **Initialize Git and push**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Personal website"
   git branch -M main
   git remote add origin https://github.com/selfishout/selfishout.github.io.git
   git push -u origin main
   ```

4. **Your website will be live at: `https://selfishout.github.io`**
   - Usually takes 1-2 minutes to go live
   - Check https://github.com/selfishout/selfishout.github.io/settings/pages

### Method 2: Use Existing Repository with GitHub Pages

1. Create a repository (any name, e.g., `personal-website`)
2. Push your code
3. Go to Settings → Pages
4. Source: Deploy from branch `main`
5. Folder: `/root`
6. Save

Your site will be at: `https://selfishout.github.io/personal-website`

## 🔧 Quick Setup Script

Run this command to deploy your website:

```bash
cd "/Users/alitorabi/Documents/Projects/pythonProject/GitHub Portfolio Projects/personal-website"

# Make sure you've created the repository: selfishout.github.io on GitHub first!

git init
git add .
git commit -m "Initial commit: Professional personal website

Features:
- Modern, responsive design
- Showcases 12 CV/ML projects
- Publications and research interests
- Professional experience timeline
- Contact information
- Smooth animations and interactions"

git branch -M main
git remote add origin https://github.com/selfishout/selfishout.github.io.git
git push -u origin main
```

## ✅ Pre-Deployment Checklist

Before deploying, make sure to update:

- [ ] LinkedIn URL (index.html, line 55)
- [ ] Google Scholar URL (index.html, line 58)
- [ ] Publication links with actual URLs
- [ ] Any placeholder content
- [ ] Test locally by opening index.html in a browser

## 🌐 Testing Locally

Simply open `index.html` in your web browser:

```bash
# On Mac
open index.html

# Or drag and drop index.html into your browser
```

## 📱 Sections

Your website includes:

1. **Home/Hero** - Introduction with photo and social links
2. **About** - Background and highlights
3. **Research Interests** - 4 main research areas
4. **Projects** - Featured 6 of 12 GitHub projects (link to all 12)
5. **Publications** - 5 publications (3 published, 2 under review)
6. **Experience** - Timeline of work and research experience
7. **Contact** - Email, phone, location, GitHub

## 🎯 Next Steps After Deployment

1. **Add Google Analytics** (Optional)
   ```html
   <!-- Add before </head> in index.html -->
   <!-- Google Analytics tracking code -->
   ```

2. **Custom Domain** (Optional)
   - Buy a domain (e.g., alitorabi.com)
   - Point to your GitHub Pages
   - Add CNAME file with your domain

3. **SEO Optimization**
   - Submit to Google Search Console
   - Add sitemap.xml
   - Share on social media

4. **Regular Updates**
   - Add new publications
   - Update projects
   - Add blog posts (optional)

## 📊 Features Included

✅ Fully responsive design (mobile, tablet, desktop)
✅ Smooth scrolling navigation
✅ Animated sections (AOS library)
✅ Project showcases with links
✅ Publications list
✅ Timeline for experience
✅ Contact information
✅ Back to top button
✅ Social media links
✅ Professional color scheme
✅ Fast loading
✅ SEO optimized
✅ Keyboard shortcuts (H=Home, C=Contact)

## 🛠️ Technologies Used

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid & Flexbox
- **JavaScript** - Interactive features
- **AOS** - Animate On Scroll library
- **Font Awesome** - Icons
- **Google Fonts** - Inter & JetBrains Mono

## 📄 License

This website template is created for Ali Torabi's personal use. Feel free to customize it for your needs.

## 📧 Support

If you encounter any issues:
1. Check the GitHub Pages deployment status
2. Ensure all file paths are correct
3. Verify the repository name is exactly `selfishout.github.io`
4. Wait 2-3 minutes after pushing for the site to go live

## 🎉 Your Website is Ready!

Your professional personal website includes:
- Modern, eye-catching design
- All your research and projects
- Professional experience
- Publications list
- Easy contact methods
- Links to your 12 GitHub projects

**Deploy it now and share it with the world!** 🚀

---

**Created for Ali Torabi**
PhD Student in Computer Science
University of Wyoming

Website: https://selfishout.github.io (after deployment)
GitHub: https://github.com/selfishout
Email: atorabi@uwyo.edu

