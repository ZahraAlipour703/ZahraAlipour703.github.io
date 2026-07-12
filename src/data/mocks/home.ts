// Content for the home page. Ported from the previous static site
// (zahraalipour703.github.io). Replace with a CMS/API source later if needed.

export const siteMeta = {
  name: "Zahra Alipour",
  role: "Computer Vision Engineer",
  tagline: "Computer Vision Engineer & AI Researcher",
  focus: "Computer Vision, Deep Learning",
  location: "Karaj, IR",
  email: "zahraalipour.ac@gmail.com",
  phone: "+98 (919) 703-4891",
  github: "https://github.com/ZahraAlipour703",
  linkedin: "https://www.linkedin.com/in/zahraalipourr",
  // TODO(zahra): swap in the real Google Scholar citations ID
  scholar: "https://scholar.google.com/citations?user=YOUR_ID",
};

export const navLinks = [
  { label: "Home", href: "#home" },
  { label: "About", href: "#about" },
  { label: "Research", href: "#research" },
  { label: "Projects", href: "#projects" },
  { label: "Publications", href: "#publications" },
  { label: "Experience", href: "#experience" },
  { label: "Contact", href: "#contact" },
];

export const aboutParagraphs = [
  "I am a Computer Vision Engineer and AI Researcher with a background in Biomedical Engineering (Biomechanics). My research focuses on developing intelligent visual perception systems using deep learning, foundation vision models, and multimodal AI for real-world applications.",
  "My work spans computer vision, medical image analysis, robotics, human pose estimation, and vision-language models. I've built real-time systems using YOLO, MediaPipe, OpenCV, SAM/SAM2, Grounding DINO, and modern deep learning frameworks for robotic control, healthcare, and intelligent perception.",
  "My long-term research interests include foundation models, embodied AI, medical imaging, explainable computer vision, and multimodal scene understanding, with GPU-optimized scaling for large-scale datasets such as PASCAL VOC and COCO.",
];

export const aboutHighlights = [
  {
    id: "education",
    label: "Education",
    detail: "B.Sc. in Biomedical Engineering",
    sub: "Qazvin Islamic Azad University",
  },
  {
    id: "focus",
    label: "Research Focus",
    detail: "AI",
    sub: "Computer Vision",
  },
  {
    id: "recognition",
    label: "Recognition",
    detail: "ICRoM 2025 Publication",
    sub: "Rank 28th, QIAU entrance 2019 — BME",
  },
];

export const researchInterests = [
  {
    id: "wsss",
    class: "segmentation",
    confidence: 0.94,
    title: "Weakly Supervised Semantic Segmentation",
    description:
      "Developing novel CAM-based techniques with influence functions for improved segmentation with weak annotations.",
  },
  {
    id: "xai",
    class: "explainability",
    confidence: 0.91,
    title: "Explainable AI for Computer Vision",
    description:
      "Creating interpretable deep learning models with explanation methods to improve neural network predictions.",
  },
  {
    id: "vit",
    class: "transformer",
    confidence: 0.97,
    title: "Vision Transformers & Deep Learning",
    description:
      "Exploring transformer architectures for computer vision tasks and multi-modal learning applications.",
  },
  {
    id: "gpu",
    class: "infra",
    confidence: 0.89,
    title: "GPU-Accelerated ML",
    description:
      "Optimizing model training with CUDA, mixed-precision training, and multi-GPU parallelism for large-scale datasets.",
  },
];

export const projects = [
  {
    id: "vit-classification",
    title: "Vision Transformer Classification",
    description:
      "Complete PyTorch implementation of ViT with attention visualization and transfer learning capabilities.",
    tags: ["PyTorch", "Transformers", "ViT"],
    href: null,
  },
  {
    id: "clip-search",
    title: "CLIP Image Search Engine",
    description:
      "Semantic image search using OpenAI CLIP for natural language queries with FAISS integration.",
    tags: ["CLIP", "FAISS", "Gradio"],
    href: null,
  },
  {
    id: "vlm-captioning",
    title: "Image Captioning with VLMs",
    description:
      "Automatic caption generation using BLIP, BLIP-2, and GIT vision-language models.",
    tags: ["BLIP", "VLM", "Hugging Face"],
    href: null,
  },
  {
    id: "yolo-detection",
    title: "YOLO Object Detection",
    description:
      "Real-time object detection with YOLOv8 supporting 80+ classes with video processing.",
    tags: ["YOLOv8", "Real-time", "OpenCV"],
    href: null,
  },
  {
    id: "semantic-segmentation",
    title: "Semantic Segmentation",
    description:
      "Pixel-level classification using DeepLabV3 with 21-class PASCAL VOC segmentation.",
    tags: ["DeepLab", "Segmentation", "PyTorch"],
    href: null,
  },
  {
    id: "survival-prediction",
    title: "Survival Prediction (Feedforward Neural Network)",
    description:
      "Predicting Titanic passenger survival with an FFNN — data preprocessing, feature scaling, training, evaluation, and hyperparameter tuning via Random Search and Keras Tuner.",
    tags: ["EDA", "Data Processing", "FNN"],
    href: "https://github.com/ZahraAlipour703/titanic.git",
  },
];

export const publications = [
  {
    id: "litehand-yolo",
    year: "2025",
    title:
      "LiteHand-YOLO: Efficient Attention-Enhanced YOLOv8n for Robust Hand Tracking",
    authors: "Zahra Alipour",
    venue: null,
    href: null,
    status: "published" as const,
  },
];

export const experience = [
  {
    id: "cv-research-engineer",
    date: "Dec 2024 — Jun 2026",
    role: "Computer Vision Research Engineer",
    org: "AstraBionics",
    bullets: [
      "Developed an integrated YOLOv8 + MediaPipe pipeline for real-time hand tracking (99% test accuracy).",
      "Designed and implemented a real-time robotic hand motion replication system based on human hand pose estimation (YOLO-Pose, MediaPipe), improving fps by 10%.",
      "Implemented stereo-vision camera calibration and 3D ArUco marker tracking for precise hand motion estimation in biomechanical applications, with under 2° error.",
      "Applied real-time human body pose estimation (YOLO models) to exercise movement analysis, enabling motion feedback for rehabilitation scenarios.",
    ],
  },
  {
    id: "ml-intern",
    date: "Jul 2024 — Dec 2024",
    role: "Machine Learning Intern",
    org: "AstraBionics",
    bullets: [
      "Analyzed and computed joint angles (MCP, PIP, DIP) for human and robotic index finger movement.",
      "Classified flexion vs. extension movements on the NinaPro dataset using a Time-Delay Neural Network (TDNN), achieving 85% accuracy.",
      "Pre-processed IMU and tracker data for synchronization and integrated the robotic finger tracking pipeline.",
    ],
  },
];

export const contactChannels = [
  { id: "email", label: "Email", value: siteMeta.email, href: `mailto:${siteMeta.email}` },
  { id: "phone", label: "Phone", value: siteMeta.phone, href: null },
  { id: "location", label: "Location", value: siteMeta.location, href: null },
  {
    id: "github",
    label: "GitHub",
    value: "@ZahraAlipour703",
    href: siteMeta.github,
  },
];
