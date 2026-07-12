# 🚀 Quick Start Guide

Get your professional website live in **5 minutes**!

## Step 1: Create GitHub Repository (2 minutes)

1. Go to: **https://github.com/new**

2. Fill in:
   - **Repository name**: `selfishout.github.io` (MUST be exactly this!)
   - **Description**: "Personal Website - Computer Vision & Deep Learning Researcher"
   - **Public**: ✅ Yes
   - **Add README**: ❌ No
   - **Add .gitignore**: ❌ No
   - **Choose a license**: ❌ No

3. Click **"Create repository"**

## Step 2: Deploy Your Website (2 minutes)

Open Terminal and run:

```bash
cd "/Users/alitorabi/Documents/Projects/pythonProject/GitHub Portfolio Projects/personal-website"

./deploy.sh
```

That's it! The script will automatically:
- ✅ Initialize Git
- ✅ Add all files
- ✅ Create commit
- ✅ Push to GitHub

## Step 3: Wait & Verify (1 minute)

1. **Wait 1-2 minutes** for GitHub to build your site

2. **Visit**: https://selfishout.github.io

3. **Verify deployment**:
   - Check: https://github.com/selfishout/selfishout.github.io/actions
   - Settings: https://github.com/selfishout/selfishout.github.io/settings/pages

## ✅ Your Website is Live!

### What You Have

✨ **A professional website with:**
- Modern, responsive design
- All 12 of your GitHub projects
- Your publications and research
- Professional experience timeline
- Contact information
- Smooth animations

### URLs to Share

- **Website**: https://selfishout.github.io
- **GitHub Profile**: https://github.com/selfishout
- **All Projects**: https://github.com/selfishout?tab=repositories

---

## 🎯 Optional: Customize Before Deploying

If you want to update social links first:

### 1. Edit LinkedIn Profile

Open `index.html` and update line 55:

```html
<!-- Change this: -->
<a href="https://linkedin.com/in/yourprofile" target="_blank">

<!-- To your actual LinkedIn: -->
<a href="https://linkedin.com/in/ali-torabi-xyz" target="_blank">
```

### 2. Add Google Scholar

Update line 58:

```html
<a href="https://scholar.google.com/citations?user=YOUR_ID" target="_blank">
```

### 3. Update Publication Links

Add actual URLs to your publications in the Publications section.

Then run `./deploy.sh` to deploy!

---

## 🆘 Troubleshooting

### "Repository doesn't exist"
→ Make sure you created `selfishout.github.io` on GitHub first

### "Authentication failed"
→ Run: `gh auth login` and follow the prompts

### "Site not loading"
→ Wait 2-3 minutes, GitHub takes time to build
→ Check: https://github.com/selfishout/selfishout.github.io/settings/pages

### Need to update something?
```bash
# Edit your files, then:
cd "/Users/alitorabi/Documents/Projects/pythonProject/GitHub Portfolio Projects/personal-website"
git add .
git commit -m "Update: description of what you changed"
git push
```

---

## 📱 Share Your Website

### On LinkedIn:
```
🚀 Excited to share my personal website!

Showcasing my research in Computer Vision, Deep Learning, and Explainable AI, 
along with 12 production-ready projects.

Check it out: https://selfishout.github.io

#ComputerVision #DeepLearning #MachineLearning #AI #PhD #Research
```

### On Twitter:
```
Just launched my personal website! 🎉

✨ Computer Vision research
🧠 12 ML/DL projects
📄 Publications
🔗 https://selfishout.github.io

#MachineLearning #ComputerVision #DeepLearning
```

### In Your Resume:
```
Website: https://selfishout.github.io
GitHub: https://github.com/selfishout
```

---

## 🎉 Success Checklist

After deployment, your website will have:

- ✅ Professional, modern design
- ✅ Mobile-responsive layout
- ✅ Your profile photo
- ✅ Research interests
- ✅ 12 GitHub projects showcase
- ✅ Publications list
- ✅ Experience timeline
- ✅ Contact information
- ✅ Social media links
- ✅ Smooth animations
- ✅ SEO optimized

**You're ready to impress recruiters and the research community!** 🌟

---

## 💡 Pro Tips

1. **Add to Resume**: Put https://selfishout.github.io on your resume header

2. **Email Signature**: Add your website link to your email signature

3. **Share Widely**: LinkedIn, Twitter, academic profiles

4. **Keep Updated**: Add new publications and projects regularly

5. **Track Visitors**: Consider adding Google Analytics (optional)

---

**Questions?**
- Check README.md for detailed documentation
- All files are in: `/Users/alitorabi/Documents/Projects/pythonProject/GitHub Portfolio Projects/personal-website/`

**Ready to deploy?** Run `./deploy.sh` now! 🚀

