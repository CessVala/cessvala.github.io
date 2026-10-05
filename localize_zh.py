"""Generate Simplified Chinese counterparts for the static preview pages.

English pages remain the source of truth. Run `python localize_zh.py` after
editing them; the language switch is also regenerated on every page.
"""
from pathlib import Path
from lxml import html
from datetime import date
import yaml
import re

ROOT = Path(__file__).parent / "dist"

UI = {
    "Home": "首页", "Research": "研究", "Publications": "论文", "Announcements": "动态",
    "About Me": "关于我", "Teaching & Outreach": "教学与学术交流", "Contact": "联系我",
    "Honors & Community": "荣誉与学术服务",
    "Download CV": "下载简历", "CV ↗": "简历 ↗", "Read more →": "了解更多 →",
    "Read more ↗": "了解更多 ↗", "All announcements": "全部动态",
    "Next older announcement →": "下一篇动态 →", "Manuscripts": "论文发表",
    "Preprints": "预印本", "Read the Manuscript ↗": "阅读论文 ↗",
    "Read the Preprint ↗": "阅读预印本 ↗", "Read the Manuscript": "阅读论文",
    "Read the paper →": "阅读论文 →", "About:": "简介：", "Latest:": "最新进展：",
    "Microscopy, image analysis, and collaborative research.": "显微成像、图像分析与合作研究。",
    "Let’s talk science.": "欢迎交流科研想法。",
    "Cesar Valades-Cruz": "Cesar Valades-Cruz",
    "Current focus": "当前研究", "Imaging methods": "成像方法",
    "Computational tools": "计算工具", "← Research overview": "← 研究概览",
    "01 / CURRENT FOCUS": "01 / 当前研究", "02 / IMAGING METHODS": "02 / 成像方法",
    "03 / COMPUTATIONAL TOOLS": "03 / 计算工具",
    "Bioimage analysis · Advanced microscopy · Artificial intelligence": "生物图像分析 · 先进显微成像 · 人工智能",
    "Microscopy × quantitative analysis": "显微成像 × 定量分析",
    "Cyanobacterial cell division": "蓝细菌细胞分裂",
    "Polarization & super-resolution": "偏振与超分辨成像",
    "3D live-cell image analysis": "活细胞三维图像分析",
    "Associate Researcher · Institute of Hydrobiology, CAS": "中国科学院水生生物研究所副研究员",
    "Wuhan, China": "中国武汉",
    "Based in": "所在地", "Current role": "现任职务", "Background": "研究背景",
    "Focus": "研究方向", "Biophotonics · microscopy · image analysis": "生物光子学 · 显微成像 · 图像分析",
    "Microscopy · image analysis · cell biology": "显微成像 · 图像分析 · 细胞生物学",
    "Nature Communications · Co-first author": "Nature Communications · 共同第一作者",
    "Communications Biology · Co-first author": "Communications Biology · 共同第一作者",
    "Nature Protocols · Co-first author": "Nature Protocols · 共同第一作者",
    "Nature Methods · Co-first author": "Nature Methods · 共同第一作者",
    "Leader": "负责人", "Subtask leader": "子课题负责人", "Participant": "参与者",
}

COMMON = {
    "Segmentation and tracking of individual cells and filaments to study growth, division, and differentiation.": "通过对单个细胞和藻丝进行分割与追踪，研究其生长、分裂和分化。",
    "Measuring molecular orientation and nanoscale structure using polarized super-resolution microscopy.": "利用偏振超分辨显微成像测量分子取向与纳米尺度结构。",
    "Navigation, tracking, restoration, and data workflows for complex microscopy datasets.": "针对复杂显微图像数据开展浏览、追踪、图像复原与分析流程研究。",
    "Automated segmentation, tracking, and quantitative analysis of cells and filaments to study growth and differentiation.": "通过自动分割、追踪和定量分析细胞与藻丝，研究生长和分化。",
    "Measuring molecular orientation and nanoscale structure in actin networks and other biological assemblies.": "测量肌动蛋白网络及其他生物结构中的分子取向和纳米结构。",
    "Restoration, tracking, visualization, and data workflows for complex microscopy datasets.": "为复杂显微数据开发图像复原、追踪、可视化及分析流程。",
    "Advanced microscopy and image analysis for quantitative cell biology.": "利用先进显微成像和图像分析开展定量细胞生物学研究。",
    "Read the paper →": "阅读论文 →",
}

PAGES = {
    "": {
        "I’m Cesar Valades-Cruz, an associate researcher at the Institute of Hydrobiology, Chinese Academy of Sciences. I develop microscopy and AI-assisted bioimage analysis methods to understand how cells organize, move, and divide.": "我是中国科学院水生生物研究所的副研究员 Cesar Valades-Cruz。我开发显微成像和人工智能辅助的生物图像分析方法，研究细胞如何组织、运动和分裂。",
        "Explore research": "探索研究", "Get in touch": "与我联系",
        "From images to insight": "从图像走向发现",
        "My work connects optical imaging, computational methods, and cell biology across three complementary areas.": "我的研究将光学成像、计算方法与细胞生物学结合，主要涵盖以下三个方向。",
        "Full research overview ↗": "查看研究概览 ↗",
        "At the Institute of Hydrobiology": "在中国科学院水生生物研究所",
        "Quantifying life, one cell at a time": "从单个细胞出发，定量理解生命",
        "My current research studies how cyanobacterial cells grow and divide. Image analysis lets us follow individual cells within filaments and connect their behavior to larger biological patterns.": "我目前研究蓝细菌细胞的生长和分裂。借助图像分析，我们可以追踪藻丝中的单个细胞，并将其行为与更大尺度的生物学规律联系起来。",
        "Explore this work ↗": "了解这项研究 ↗", "Latest news": "最新动态",
        "View all announcements →": "查看全部动态 →", "Selected publications": "精选论文",
        "Recent and representative work": "近期与代表性研究", "View full publication list ↗": "查看完整论文列表 ↗",
        "Biology meets optics and computation.": "生物学与光学、计算科学的交汇。",
        "My path has taken me from mechatronics in Mexico to biophotonics in France and Spain, then to cell imaging at Institut Curie and Inria. Today I work in Wuhan, China, with Prof. Cheng-Cai Zhang’s team.": "我的研究经历始于墨西哥的机电一体化，随后在法国和西班牙从事生物光子学研究，并在居里研究所和 Inria 开展细胞成像工作。如今，我在中国武汉张承才教授团队工作。",
        "I enjoy building tools that turn difficult microscopy data into useful biological measurements, and collaborating across disciplines to make those methods available to others.": "我喜欢开发工具，把复杂的显微数据转化为有意义的生物学测量结果，并通过跨学科合作让更多人能够使用这些方法。",
        "About": "关于我",
    },
    "research": {
        "I develop microscopy and image analysis methods to study cell organization across scales. Explore the three areas below for an overview of the questions, methods, and projects.": "我开发显微成像与图像分析方法，研究不同尺度上的细胞组织方式。以下三个方向介绍相关科学问题、方法与项目。",
        "My current work at the Institute of Hydrobiology centers on cyanobacterial cell division. Collaborations in polarization imaging and computational microscopy extend these methods to molecular organization and live-cell data.": "我目前在水生生物研究所的工作聚焦蓝细菌细胞分裂。通过偏振成像与计算显微学的合作，我也将这些方法用于研究分子组织及活细胞数据。",
        "Funding & collaborations": "资助与合作", "Funded research projects": "资助项目",
        "Selected projects and programs in which I participate. See the CV for the full record.": "以下是我参与的部分项目；完整记录请参阅简历。",
        "NSFC Research Fund for International Excellent Young Scientists": "国家自然科学基金外国优秀青年学者研究基金",
        "CAS Class B Strategic Priority Research Program": "中国科学院战略性先导科技专项（B类）",
        "NSFC Key Project": "国家自然科学基金重点项目", "NSFC Special Project": "国家自然科学基金专项项目",
        "Applications of Biophotonics and Image Processing in Microbiology · W2632090": "生物光子学与图像处理在微生物学中的应用 · W2632090",
        "High-throughput screening technologies for endosymbiosis.": "面向内共生研究的高通量筛选技术。",
        "Three-dimensional regulation of cell division in multicellular cyanobacteria · 32330003": "多细胞蓝细菌细胞分裂的三维调控 · 32330003",
        "Establishing cell function editing technology based on endosymbiosis · 32350028": "建立基于内共生的细胞功能编辑技术 · 32350028",
        "Polarization microscopy for imaging of membrane organization.": "利用偏振显微成像研究细胞膜组织。",
        "Image-guided navigation and visualization of large live-cell microscopy datasets.": "大规模活细胞显微数据的图像引导浏览与可视化。",
        "Data assimilation and lattice light-sheet imaging for endocytosis and exocytosis modeling.": "结合数据同化与晶格光片显微成像研究内吞和胞吐过程。",
    },
    "research/current-focus": {
        "Cell division of cyanobacteria": "蓝细菌细胞分裂", "Cell segmentation": "细胞分割",
        "About: I develop automatic tracking methods for single cells, filaments, and cell populations of cyanobacteria, combining advanced microscopy with deep learning to study cell division mechanisms and growth dynamics.": "简介：我结合先进显微成像与深度学习，开发蓝细菌单细胞、藻丝和细胞群体的自动追踪方法，研究细胞分裂机制及生长动态。",
    },
    "research/imaging-methods": {
        "Quantitative nanoscale imaging of molecular orientation": "分子取向的纳米尺度定量成像",
        "Ultrastructure imaging": "超微结构成像",
        "About: Long-standing collaboration with Sophie Brasselet’s team at Institut Fresnel, France. We develop polarization-based super-resolution methods to measure the nanoscale organization and 3D orientation of biological filaments such as actin networks.": "简介：我与法国菲涅耳研究所 Sophie Brasselet 团队长期合作，开发偏振超分辨成像方法，测量肌动蛋白网络等生物纤维的纳米尺度组织与三维取向。",
        "Latest: Our new method 4polar3D, published in Nature Communications (2026), enables 3D orientation measurements of single molecules in dense actin structures using ratiometric polarization splitting — with minimal optical complexity and fast data processing. Read the paper →": "最新进展：我们在 Nature Communications（2026）发表的 4polar3D 方法，通过偏振比例分束，以简洁的光学配置和快速的数据处理，测量致密肌动蛋白结构中单分子的三维取向。阅读论文 →",
    },
    "research/computational-tools": {
        "3D+time live cell imaging": "活细胞三维动态成像",
        "3D spots and cell segmentation": "三维斑点检测与细胞分割",
        "Image preprocessing and data management": "图像预处理与数据管理",
        "LLSM and 3D single particle tracking": "晶格光片显微成像与三维单粒子追踪",
        "About: INRIA IPL project combining machine learning-driven detection of regions of interest with automatic quantification of molecular interactions and cell processes, enabling efficient navigation of large 3D+time datasets.": "简介：Inria IPL 项目结合机器学习驱动的感兴趣区域检测与分子相互作用和细胞过程的自动定量分析，帮助研究人员高效浏览大型三维动态数据集。",
        "About: Analysis of clathrin-mediated and glyco(sphingo)lipid/lectin (GL-Lect)-mediated endocytosis using Lattice Light-Sheet Microscopy (LLSM) and 3D single particle tracking.": "简介：利用晶格光片显微成像和三维单粒子追踪，分析网格蛋白介导以及糖脂／凝集素（GL-Lect）介导的内吞过程。",
        "About: Project of the Serpico-STED Team within the National Research Infrastructure France BioImaging, providing an integrative platform for image data management and analysis across the 18 imaging facilities of the infrastructure.": "简介：Serpico-STED 团队参与法国国家生物成像基础设施项目，开发覆盖其 18 个成像设施的图像数据管理与分析集成平台。",
    },
    "about": {
        "A short introduction to my work and the path that brought me to microscopy and image analysis.": "简要介绍我的研究，以及我如何走向显微成像与图像分析领域。",
        "I am Cesar Augusto Valades-Cruz, a bioimage analyst and associate researcher at the Institute of Hydrobiology, Chinese Academy of Sciences, in Wuhan. I develop microscopy and image analysis methods to study how cells organize, grow, and divide.": "我是 César Augusto Valades-Cruz，现任中国科学院水生生物研究所副研究员，主要从事生物图像分析。我开发显微成像与图像分析方法，研究细胞的组织、生长和分裂。",
        "I enjoy working with biologists, physicists, and software developers to turn complex images into useful biological measurements.": "我乐于与生物学家、物理学家和软件开发者合作，从复杂图像中提取有用的生物学测量结果。",
        "My work connects optics, computation, and cell biology. I began with polarized super-resolution microscopy during my PhD in France and Spain, then studied endocytosis and live-cell imaging at Institut Curie and Inria. Today, I apply advanced imaging and quantitative analysis to cyanobacterial cell division and differentiation.": "我的工作连接光学、计算科学与细胞生物学。博士期间，我在法国和西班牙研究偏振超分辨显微成像；随后在居里研究所和 Inria 研究内吞作用与活细胞成像。如今，我运用先进成像和定量分析研究蓝细菌细胞分裂与分化。",
        "My path": "我的经历", "Biophotonics": "生物光子学", "Live-cell imaging": "活细胞成像",
        "Quantitative microbiology": "定量微生物学",
        "Doctoral research in polarized super-resolution microscopy with Sophie Brasselet at Institut Fresnel, Aix-Marseille University, and Pablo Loza Alvarez at ICFO, Universitat Politècnica de Catalunya.": "在法国艾克斯—马赛大学菲涅耳研究所与 Sophie Brasselet，以及西班牙加泰罗尼亚理工大学 ICFO 的 Pablo Loza Alvarez 合作开展偏振超分辨显微成像的博士研究。",
        "Studied the mechanisms of endocytosis and intracellular trafficking with Ludger Johannes at Institut Curie, using advanced microscopy. Developed image analysis, deep learning, and computational methods for light-sheet microscopy with Jean Salamero (Institut Curie) and Charles Kervrann (Inria), as part of France BioImaging.": "在居里研究所与 Ludger Johannes 合作，利用先进显微成像研究内吞作用与细胞内运输机制。在 France BioImaging 框架下，与 Jean Salamero（居里研究所）和 Charles Kervrann（Inria）合作，开发用于光片显微成像的图像分析、深度学习及计算方法。",
        "Imaging and image analysis of cyanobacterial growth and cell division with Prof. Cheng-Cai Zhang’s team at the Institute of Hydrobiology.": "在水生生物研究所张承才教授团队，利用成像与图像分析研究蓝细菌生长和细胞分裂。",
        "Teaching & Outreach →": "教学与学术交流 →", "Full CV ↗": "完整简历 ↗",
    },
    "academic-activities": {
        "Teaching, mentoring, conferences, and workshops.": "教学、学生指导、学术会议与研讨会。",
        "Teaching & mentoring": "教学与指导", "Conferences & workshops": "会议与研讨会",
        "Honors & fellowships": "荣誉与奖学金", "Community & peer review": "学术服务与同行评审",
        "Student supervision": "学生指导",
        "Supervising Master’s and PhD students at the Institute of Hydrobiology, CAS, in microscopy and quantitative analysis of cyanobacteria.": "在中国科学院水生生物研究所指导硕士和博士研究生开展显微成像及蓝细菌定量分析研究。",
        "University lecturer · Tec de Monterrey": "大学授课 · 蒙特雷理工大学",
        "Taught Physics I and II, Introduction to Physics, Physics for Design, and Differential Equations, alongside physics and electricity and magnetism laboratories.": "讲授物理学 I 与 II、物理学导论、设计专业物理学和微分方程，并指导物理及电磁学实验。",
        "Selected presentations and workshops from my CV.": "以下选自我的简历中的报告与研讨会经历。",
        "Image analysis framework for filamentous cyanobacteria: preprocessing, segmentation and tracking.": "丝状蓝细菌图像分析框架：预处理、分割与追踪。",
        "Image analysis framework for filamentous cyanobacteria: preprocessing, segmentation, tracking and 3D volume estimation.": "丝状蓝细菌图像分析框架：预处理、分割、追踪及三维体积估计。",
        "Assessing the reproducibility of a bioimage analysis workflow characterising tissue flow in Drosophila.": "评估果蝇组织流动生物图像分析流程的可重复性。",
        "Advanced microscopy and image processing for biological applications.": "面向生物学应用的先进显微成像与图像处理。",
        "Data management and analysis tools at the Light Sheet Fluorescence Microscopy workshop.": "光片荧光显微成像研讨会上的数据管理与分析工具。",
        "Special Expert.": "特需外国人才。",
        "Mexican National Research System": "墨西哥国家研究人员体系",
        "SNI Level 1 (2020–2024); Candidato through the Mexican Diaspora Chairs Program (appointment begins in 2027).": "2020—2024 年为 SNI 一级；通过墨西哥侨民讲席计划获 Candidato 资格（2027 年起）。",
        "Graduate fellowships": "研究生阶段奖学金",
        "Erasmus Mundus PhD fellowship (2010–2014); Erasmus Mundus and CONACyT Master’s fellowships (2008–2010).": "Erasmus Mundus 博士奖学金（2010—2014）；Erasmus Mundus 和 CONACyT 硕士奖学金（2008—2010）。",
        "GloBIAS Scientific Advisory Committee": "GloBIAS 科学顾问委员会",
        "Elected member of the Global Bioimage Analysis Society’s Scientific Advisory Committee.": "当选全球生物图像分析学会科学顾问委员会委员。",
        "Peer review": "同行评审", "Journal reviewer": "期刊审稿人",
        "Review assignments for Nature Communications, Bioinformatics, PLOS Computational Biology, Journal of Physical Chemistry Letters, and Journal of Visualized Experiments.": "为 Nature Communications、Bioinformatics、PLOS Computational Biology、Journal of Physical Chemistry Letters 和 Journal of Visualized Experiments 等期刊审稿。",
    },
    "contact": {
        "Get in touch about microscopy, image analysis, cyanobacterial cell biology, or research collaborations.": "欢迎就显微成像、图像分析、蓝细菌细胞生物学或科研合作与我联系。",
        "Write to me": "写信给我", "Email": "电子邮箱",
        "The easiest way to reach me is by email.": "通过电子邮件联系我最方便。",
        "Affiliation": "工作单位", "Institute of Hydrobiology": "中国科学院水生生物研究所",
        "Academic profiles": "学术主页", "Google Scholar ↗": "谷歌学术 ↗",
        "Associate Researcher": "副研究员", "Algal Growth and Development group": "藻类生长发育研究组",
        "Chinese Academy of Sciences": "中国科学院",
    },
    "publications": {
        "Research articles, methods, reviews, and proceedings.": "研究论文、方法论文、综述与会议论文。",
        "First author publications": "第一作者论文", "Corresponding author publications": "通讯作者论文",
        "Other publications": "其他论文", "Reviews, Perspective & Comments": "综述、观点与评论",
        "Proceedings": "会议论文", "Preprints and submitted papers": "预印本与投稿中论文",
        "Link": "链接",
    },
    "announcements": {
        "Publication updates and research news from Cesar Valades-Cruz.": "César Valades-Cruz 的论文动态与科研消息。",
        "Publication updates and research news, from the latest work back to 2022.": "从最新研究到 2022 年的论文动态与科研消息。",
    },
}

PAGES["honors-community"] = {
    **PAGES["academic-activities"],
    "Honors, fellowships, academic community roles, and peer review.": "荣誉、奖学金、学术团体任职与同行评审。",
}

# Keep journal names and published paper titles in English for accurate citations.
# Each Chinese announcement retains its original bibliography and external links.
NEWS = {
    "2026-07-06-bioimageit-v2-manuscript": ("BioImageIT 新版架构发表于 Journal of Microscopy", "很高兴分享 Arthur Masson 领衔，与 Sylvain Prigent、Ludovic Leconte、Léo Maury、Jean Salamero 和 Charles Kervrann 合作完成的新论文。", "研究介绍了基于 Python 的全新 BioImageIT 架构，让生物图像分析流程更易构建、共享和复现。"),
    "2026-06-28-globias-manuscript": ("GloBIAS 案例研究发表于 Journal of Microscopy", "很高兴分享与 GloBIAS 社群合作完成的新论文，通过案例研究探讨生物图像分析流程的可重复性。", "感谢通讯作者 Caterina Fuster-Barceló、Rocco D’Antuono，合作者 Mélodie Ambroset、Libert Brice Tonfack，以及 GloBIAS 社群。"),
    "2026-03-19-4polar3d-manuscript": ("4polar3D 发表于 Nature Communications", "很高兴分享我在 Nature Communications 发表的共同第一作者论文，与 Charitra S. Senthil Kumar、Miguel Sison 及法国菲涅耳研究所 Sophie Brasselet 团队合作完成。", "这种方法可在致密肌动蛋白网络中测量单分子的三维取向。"),
    "2025-10-27-glycoswitch-manuscript": ("α5β1 整合素内吞研究发表于 Nature Communications", "很高兴分享与法国居里研究所 Ludger Johannes 团队合作发表的新论文。", "我与 Ludovic Leconte、Christian Wunder、Massiullah Shafaq-Zadah 和 Estelle Dransart 共同参与晶格光片显微成像与图像分析。"),
    "2025-07-18-4polar3d-preprint": ("4polar3D 预印本发表于 bioRxiv", "很高兴分享我们在 bioRxiv 发表的新研究。我与 Charitra S. Senthil Kumar 和 Miguel Sison 共同担任第一作者。", "这项研究得益于法国菲涅耳研究所及其他合作团队的共同努力。"),
    "2025-02-26-deepcristae-manuscript": ("DeepCristae 发表于 Communications Biology", "很高兴分享与 Salomé Papereux、Ludovic Leconte、Tianyan Liu、Julien Dumont、Zhixing Chen、Jean Salamero、Charles Kervrann 和 Anaïs Badoual 合作完成的共同第一作者论文。", "我们开发了名为 DeepCristae 的卷积神经网络，用于复原低空间分辨率显微图像中的线粒体嵴。"),
    "2025-02-21-desialylation-manuscript": ("β1 整合素内吞研究发表于 Nature Cell Biology", "很高兴分享与法国居里研究所 Ludger Johannes 团队合作的新论文。", "在居里研究所开展博士后研究期间，我与同事共同负责晶格光片显微成像及图像分析。"),
    "2024-11-28-utex3055-manuscript": ("聚球藻细胞极性研究发表于 Microbiological Research", "很高兴分享与水生生物研究所的 Shang-Yu Li、Chenliu He、张承才教授和 Yiling Yang 博士合作发表的论文。", "研究对象是杆状蓝细菌 Synechococcus elongatus UTEX 3055 的趋光信号网络。"),
    "2024-09-02-hidpy-manuscript": ("Hi-D 发表于 Nature Protocols", "很高兴分享与 Roman Barth、Marwan Abdellah 和 Haitham A. Shaban 合作完成的共同第一作者论文。", "Hi-D 可检测、分类、绘制并分析活细胞中染色质及核蛋白的动态。"),
    "2023-10-27-glycoswitch-preprint": ("糖链空间重排研究发表于 bioRxiv", "很高兴分享我参与晶格光片数据分析的预印本，研究 α5β1 整合素表面的 N-糖链空间重排。", "研究探讨糖链重排如何影响内吞命运。"),
    "2023-09-13-desialylation-preprint": ("β1 整合素内吞研究发表于 bioRxiv", "很高兴分享我参与完成的最新预印本。", "研究探讨生长因子诱导的去唾液酸化如何快速调控内吞作用。"),
    "2023-07-05-deepcristae-preprint": ("DeepCristae 预印本发表于 bioRxiv", "很高兴分享与 Salomé Papereux 等同事合作完成的研究。", "我们开发了 DeepCristae 卷积神经网络，用于复原显微图像中的线粒体嵴。"),
    "2023-02-27-l1cam-manuscript": ("L1CAM 内吞研究发表于 Traffic", "很高兴分享与 Camille Lemaigre、H.-F. Renard 和 Christian Wunder 合作完成的论文。", "研究涉及 L1CAM 的非网格蛋白依赖性内吞。"),
    "2023-01-27-spitfire-manuscript": ("SPITFIR(e) 发表于 Scientific Reports", "了解我们的图像降噪与反卷积软件 SPITFIR(e)。", "该算法用于三维荧光显微图像和视频的快速降噪与反卷积。"),
    "2022-11-18-hidpy-preprint": ("Hi-D-Py 预印本发表于 bioRxiv", "很高兴分享与 Marwan Abdellah、Roman Barth 和 Haitham A. Shaban 的合作研究。", "我们用 Python 实现了开源的高分辨率扩散映射（Hi-D）工具。"),
    "2022-10-07-bioimageit-manuscript": ("BioImageIT 发表于 Nature Methods", "很高兴分享与 Sylvain Prigent 和 Ludovic Leconte 合作完成的共同第一作者论文。", "这一跨学科项目旨在促进多语言图像分析及符合 FAIR 原则的数据管理。"),
    "2022-09-13-naviscope-manuscript": ("虚拟与增强现实观点文章发表于 Frontiers in Bioinformatics", "很高兴分享 NAVISCOPE 联盟关于细胞内运输可视化的观点文章。", "文章讨论虚拟现实与增强现实在细胞内可视化中的机遇与挑战。"),
    "2022-05-27-stracking-manuscript": ("STracking 发表于 Bioinformatics", "很高兴分享我的第一篇通讯作者论文。", "STracking 是用于粒子追踪与分析的免费开源 Python 工具库。"),
    "2022-01-15-4polarstorm-manuscript": ("4polar-STORM 发表于 Nature Communications", "很高兴分享与法国菲涅耳研究所 Sophie Brasselet 团队合作完成的共同第一作者论文。", "研究展示了偏振超分辨显微成像在细胞肌动蛋白纤维组织研究中的应用。"),
}


def authored_news():
    """Let newly authored posts survive later English-to-Chinese regenerations."""
    result = {}
    folder = ROOT.parent / "content" / "announcements"
    for path in folder.glob("*.md"):
        if path.name.startswith("_"):
            continue
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            continue
        fields = yaml.safe_load(content.split("---", 2)[1])
        result[path.stem] = (fields["title_zh"], fields["summary_zh"], fields["summary_zh"])
    return result


def set_text(element, value):
    """Replace human copy, leaving any existing external links and images intact."""
    if element.tag in ("a", "span", "strong", "h1", "h2", "h3") and not len(element):
        element.text = value
    elif element.tag == "p" and not element.xpath(".//a|.//img"):
        for child in list(element):
            element.remove(child)
        element.text = value


def set_paragraph(element, value):
    """Translate a paragraph while keeping useful external text links accessible."""
    anchors = [(a.get("href"), " ".join(a.text_content().split())) for a in element.xpath(".//a[@href]")]
    for child in list(element):
        element.remove(child)
    element.text = value
    for href, label in anchors:
        if label and label not in value:
            a = html.Element("a")
            a.set("href", href)
            a.text = label + " ↗"
            a.tail = " "
            element.append(a)


def translate_simple(root, translations):
    for el in root.xpath("//main//*[self::p or self::h1 or self::h2 or self::h3 or self::strong or self::span or self::a] | //footer//*[self::p or self::strong or self::a] | //header//a"):
        value = " ".join(el.text_content().split())
        result = translations.get(value)
        if result is not None and not (el.tag == "a" and len(el)):
            set_text(el, result)


def article_translation(root, slug):
    title, intro, detail = NEWS[slug]
    hero = root.xpath("//main//section[contains(@class,'page-hero')]//h1")
    if hero:
        hero[0].text = title
    # Two layouts are present: a special 4polar3D card, and standard announcements.
    intro_el = root.xpath("//section[contains(@class,'pub-announcement')]//p[contains(@class,'pub-intro')]")
    if intro_el:
        set_paragraph(intro_el[0], intro)
        for p in root.xpath("//section[contains(@class,'pub-announcement')]//p[contains(@class,'pub-collab-text')]"):
            set_paragraph(p, detail)
        for p in root.xpath("//section[contains(@class,'pub-announcement')]//p[contains(@class,'pub-description')]"):
            set_paragraph(p, detail)
        for el in root.xpath("//section[contains(@class,'pub-announcement')]//*[contains(@class,'pub-badge') or contains(@class,'pub-collab-label')]"):
            if el.tag == "div" and not len(el):
                el.text = "合作团队" if "collab" in el.get("class", "") else "新论文"
        subtitle = root.xpath("//section[contains(@class,'page-hero')]//h1/following-sibling::p")
        if subtitle:
            subtitle[0].text = "在致密肌动蛋白网络中测量单分子三维取向的新方法。" if slug == "2026-03-19-4polar3d-manuscript" else detail
        for p in root.xpath("//section[contains(@class,'pub-announcement')]//div[contains(@class,'pub-resources')]/p"):
            set_paragraph(p, detail)
    else:
        content = root.xpath("//main//div[contains(@class,'post-content')]")
        if content:
            paragraphs = [x for x in content[0].xpath("./p") if not x.xpath(".//a|.//img")]
            for i, p in enumerate(paragraphs[:2]):
                set_paragraph(p, intro if i == 0 else detail)
    for p in root.xpath("//main//p[contains(@class,'page-subtitle')]"):
        p.text = detail
    subtitle = root.xpath("//section[contains(@class,'page-hero')]//h1/following-sibling::p")
    if subtitle and not intro_el:
        set_paragraph(subtitle[0], detail)
    eyebrow = root.xpath("//main//section[contains(@class,'page-hero')]//p[contains(@class,'eyebrow')]")
    if eyebrow and eyebrow[0].text:
        d = date.fromisoformat(slug[:10])
        eyebrow[0].text = f"{d.year}年{d.month}月{d.day}日 · " + ("预印本" if "Preprints" in eyebrow[0].text else "论文发表")


def translate_news_listing(root):
    for entry in root.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' announcement ')]"):
        href = entry.get("href", "")
        slug = href.strip("/").split("/")[-1]
        if slug not in NEWS:
            continue
        title, intro, _ = NEWS[slug]
        strong = entry.xpath("./div/strong")
        if strong:
            strong[0].text = title + " →"
        spans = entry.xpath("./div/span[not(contains(@class,'category'))]")
        if spans:
            spans[-1].text = intro


def localize_page(path, source):
    relative = path.parent.relative_to(ROOT)
    key = "" if str(relative) == "." else relative.as_posix()
    root = html.fromstring(source)
    root.set("lang", "zh-CN")
    translations = {**UI, **COMMON, **PAGES.get(key, {})}
    translate_simple(root, translations)
    if key == "about":
        emphasis = [
            ["偏振超分辨显微成像", "Sophie Brasselet", "Pablo Loza Alvarez"],
            ["内吞作用与细胞内运输机制", "Ludger Johannes", "图像分析、深度学习及计算方法", "Jean Salamero", "Charles Kervrann"],
            ["蓝细菌生长和细胞分裂", "张承才教授团队"],
        ]
        paragraphs = root.xpath("//div[contains(@class,'compact-timeline')]//article/p")
        for paragraph, terms in zip(paragraphs, emphasis):
            parts = re.split("(" + "|".join(re.escape(term) for term in terms) + ")", paragraph.text_content())
            for child in list(paragraph):
                paragraph.remove(child)
            paragraph.text = parts[0]
            for i in range(1, len(parts), 2):
                strong = html.Element("strong")
                strong.text = parts[i]
                strong.tail = parts[i + 1]
                paragraph.append(strong)
    if key == "":
        eyebrow = root.xpath("//main//section[contains(@class,'hero')]//div[contains(@class,'eyebrow')]")
        if eyebrow:
            eyebrow[0].text = "生物图像分析 · 先进显微成像 · 人工智能"
        headline = root.xpath("//main//section[contains(@class,'hero')]//h1")
        if headline:
            headline[0].text = "观察细胞，"
            italic = headline[0].xpath("./em")
            if italic:
                italic[0].text = "跨越时空。"
    if key == "research/imaging-methods":
        latest = root.xpath("//main//p[strong[contains(text(),'最新进展')]]")
        if latest:
            set_paragraph(latest[0], "最新进展：我们在 Nature Communications（2026）发表的 4polar3D 方法，通过偏振比例分束，以简洁的光学配置和快速的数据处理，测量致密肌动蛋白结构中单分子的三维取向。")
    for caption in root.xpath("//main//p/img/following-sibling::em"):
        original = " ".join(caption.text_content().split())
        result = translations.get(original)
        if result:
            caption.text = result
    if key == "contact":
        for el in root.xpath("//main//section[contains(@class,'contact-card')]//p"):
            for text_node in el.xpath(".//text()"):
                translated = translations.get(str(text_node))
                if translated:
                    if text_node.is_text:
                        text_node.getparent().text = translated
                    else:
                        text_node.getparent().tail = translated
    if key in ("academic-activities", "honors-community"):
        for note in root.xpath("//main//p[contains(@class,'section-note')][a[contains(@href,'CV_')]]"):
            note.text = "完整的论文、项目和任职经历，请参阅"
            note.xpath("./a")[0].text = "简历 ↗"
            note.xpath("./a")[0].tail = "。"
    if key.startswith("announcements/"):
        article_translation(root, key.split("/")[-1])
    if key in ("", "announcements"):
        translate_news_listing(root)
    for time in root.xpath("//main//time[@datetime]"):
        try:
            d = date.fromisoformat(time.get("datetime")[:10])
            time.text = f"{d.year}年{d.month}月{d.day}日"
        except ValueError:
            pass
    # The published bibliographic titles, author names, journal names and CV stay original.
    for entry in root.xpath("//main//span[contains(@class,'pub-title')]"):
        original = " ".join((entry.text or "").split())
        title_map = {
            "4polar3D: single-molecule orientation imaging in dense actin networks": "4polar3D：致密肌动蛋白网络的单分子取向成像",
            "DeepCristae: restoring mitochondria cristae in live microscopy images": "DeepCristae：复原活细胞显微图像中的线粒体嵴",
            "Genome-wide analysis of chromatin and nuclear proteins with Hi-D": "Hi-D：全基因组染色质与核蛋白分析",
            "BioImageIT: open-source framework for integrating image data management and analysis": "BioImageIT：图像数据管理与分析的开源框架",
            "4polar-STORM: polarized super-resolution imaging of actin organization": "4polar-STORM：肌动蛋白结构的偏振超分辨成像",
        }
        if original in title_map:
            entry.text = title_map[original]
    head = root.xpath("//head")[0]
    title = head.find("title")
    if title is not None:
        title.text = "中文版 · " + title.text
    meta = root.xpath("//meta[@name='description']")
    if meta:
        meta[0].set("content", "Cesar Valades-Cruz 的个人科研网站中文版：显微成像、生物图像分析与细胞生物学。")
    for text_node in root.xpath("//text()"):
        if "César" in str(text_node):
            parent = text_node.getparent()
            if text_node.is_text:
                parent.text = str(text_node).replace("César", "Cesar")
            elif text_node.is_tail:
                parent.tail = str(text_node).replace("César", "Cesar")
    return root


def switch(root, target, chinese):
    nav = root.xpath("//header//div[contains(@class,'navlinks')]")[0]
    lang = html.Element("a")
    lang.set("class", "language-switch")
    lang.set("href", target)
    lang.set("hreflang", "en" if chinese else "zh-CN")
    lang.set("lang", "en" if chinese else "zh-CN")
    lang.set("aria-label", "Switch to English" if chinese else "切换到简体中文")
    lang.text = "EN" if chinese else "中文"
    if chinese:
        for link in root.xpath("//a[@href]"):
            href = link.get("href")
            if href.startswith("/") and not href.startswith(("/assets/", "/images/", "/files/", "/zh/")):
                link.set("href", "/zh" + href)
        for resource in root.xpath("//*[@src]"):
            src = resource.get("src")
            if src.startswith("assets/"):
                resource.set("src", "/" + src)
    nav.append(lang)
    css = root.xpath("//head/style")
    if css:
        css[0].text += LANGUAGE_CSS
    other = html.Element("link")
    other.set("rel", "alternate")
    other.set("hreflang", "en" if chinese else "zh-CN")
    other.set("href", target)
    root.xpath("//head")[0].append(other)
    return root


def render(root):
    return "<!doctype html>\n" + html.tostring(root, encoding="unicode", method="html")


LANGUAGE_CSS = "\n.navlinks .language-switch{display:inline-flex;align-items:center;justify-content:center;border:1px solid #9aa9bb;border-radius:4px;padding:4px 9px;color:white;font-size:.85rem;white-space:nowrap}html[lang='zh-CN'] body{font-family:system-ui,-apple-system,'PingFang SC','Microsoft YaHei',sans-serif}html[lang='zh-CN'] .eyebrow,html[lang='zh-CN'] .kicker{letter-spacing:.06em}"


def main():
    authored = authored_news()
    NEWS.update(authored)
    english = sorted(p for p in ROOT.rglob("index.html") if "zh" not in p.relative_to(ROOT).parts)
    for page in english:
        relative = page.parent.relative_to(ROOT)
        if len(relative.parts) == 2 and relative.parts[0] == "announcements" and relative.parts[1] in authored:
            # The bilingual Markdown builder owns both article pages.
            continue
        route = "/" if str(relative) == "." else "/" + relative.as_posix() + "/"
        zh_route = "/zh" + route
        source = page.read_text(encoding="utf-8")
        # Remove a previous generated switch so the script can be run repeatedly.
        original = html.fromstring(source)
        for el in original.xpath("//a[contains(@class,'language-switch')]|//link[@rel='alternate']"):
            el.drop_tree()
        for el in original.xpath("//style"):
            el.text = (el.text or "").replace(LANGUAGE_CSS, "")
        clean_source = render(original)
        en = switch(original, zh_route, False)
        page.write_text(render(en), encoding="utf-8")
        zh = localize_page(page, clean_source)
        switch(zh, route, True)
        dest = ROOT / "zh" / relative / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(zh), encoding="utf-8")
    print(f"Localized {len(english)} English pages into matching Chinese pages.")


if __name__ == "__main__":
    main()
