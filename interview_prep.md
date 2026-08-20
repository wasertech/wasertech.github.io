# 🎯 Préparation Entretien Coach Lab4Tech — Danny Waser

## 📖 Storytelling — Ton Récit de Carrière

### Le Fil Rouge (en 30 secondes)

> "J'ai commencé par construire un assistant vocal pour moi-même, ce qui m'a mené à contribuer au moteur de reconnaissance vocale de Mozilla (DeepSpeech → STT). De là, je suis descendu dans la stack jusqu'aux kernels GPU — j'ai merge des PR dans AutoAWQ pour la quantification de LLMs. Aujourd'hui je conçois des systèmes d'IA complets, du kernel CUDA jusqu'à l'interface utilisateur."

### Version Développée (1-2 minutes)

**Acte 1 — La découverte (2019-2021)**
> "Je suis autodidacte. Pas de diplôme d'ingénieur. J'ai un CFC commercial. Mais je passais mes nuits à bidouiller des modèles de reconnaissance vocale. J'ai réalisé que les modèles français de DeepSpeech n'étaient plus maintenus, alors j'ai pris le lead pour migrer tout le pipeline francophone vers le nouveau framework STT chez Coqui-AI. Résultat : 12 PR mergées, des modèles français publiés avec 10% de WER en moins."

**Acte 2 — La descente dans la stack (2022-2024)**
> "En travaillant sur les pipelines vocaux, j'ai buté sur les limites de l'inférence CPU. Je suis descendu dans le bas niveau : CUDA kernels, quantification de modèles. J'ai merge des PR dans AutoAWQ et AutoAWQ_kernels — du C++/CUDA pour la quantification de LLMs. Puis j'ai monté mon propre serveur d'inférence local (96GB RAM, dual RTX Titan) pour faire tourner des modèles de 70B+ paramètres en local."

**Acte 3 — La synthèse (2024-2026)**
> "Aujourd'hui je conçois des systèmes complets : des kernels CUDA optimisés pour l'inférence, des pipelines RAG, des systèmes multi-agents qui orchestrent des LLMs spécialisés, le tout sur du hardware on-premise. Je suis aussi à l'aise pour débugger un kernel Triton que pour architecturer une stack complète de déploiement LLM."

---

## 🎤 Elevator Pitch

### 30s — Version Éclair
> "Self-taught engineer with merged PRs in CUDA quantization kernels (AutoAWQ) and PyTorch internals. I build production AI systems from GPU-optimized inference down to full-stack deployment. Most recently, I've been running a multi-agent LLM orchestrator on local hardware with dual RTX Titan — combining low-level kernel optimization with end-to-end system architecture."

### 60s — Version Standard
> "I'm a self-taught AI engineer specialized in the intersection of GPU optimization and LLM systems. I have merged PRs in AutoAWQ for CUDA quantization kernels, in HuggingFace transformers, and 12 PRs in the Coqui-STT speech recognition engine. I built a production multi-agent LLM assistant running entirely on local hardware — 96GB RAM, dual RTX Titan — that handles system operations, web research, and file editing through natural language. What sets me apart is I can work at every level: optimize a CUDA kernel for quantization, design a RAG pipeline, or architect a distributed inference server. I'm equally comfortable in C++/CUDA internals as in Python application design."

### 90s — Version Détaillée
> "I'm a self-taught engineer at the intersection of GPU computing and AI systems. My work spans from CUDA kernel optimization to full-stack LLM deployment.
>
> On the low-level side, I have merged PRs in AutoAWQ — the reference implementation for AWQ quantization — where I updated the build system for CUDA kernel compilation and Torch compatibility. I also contributed to HuggingFace transformers, fixing activation initialization. And I spent 1.5 years contributing to Coqui-STT, where I led the migration of the French speech pipeline from deprecated DeepSpeech to the new framework — 12 merged PRs touching TF graph export, TFLite, memory management, and CI.
>
> On the systems side, I built and operate a production AI assistant on local hardware: 96GB RAM, dual RTX Titan, running a multi-agent orchestrator that handles system operations, web research, and file editing through natural language. I've also built custom RAG pipelines, fine-tuned LLMs, and developed quantitative trading strategies.
>
> I'm looking for work where I can leverage both skills — deep GPU internals and system architecture — to push inference performance further. That's why AfterQuery caught my attention: the opportunity to work on PyTorch internals and GPU kernels for cutting-edge inference is exactly where I want to be."

---

## ❓ Questions Fréquentes — Préparation

### "Parlez-moi de vous" / "Tell me about yourself"
→ Utilise le storytelling Acte 1-2-3 ci-dessus. Version 60s recommandée.

### "Quels sont vos points forts et faibles ?"

**Points forts :**
1. **Stack complète** — Je peux travailler du kernel CUDA jusqu'au déploiement. Peu de gens couvrent cette largeur.
2. **Autodidacte efficace** — J'ai appris CUDA et les kernels GPU par moi-même, avec des résultats concrets (PR mergées).
3. **Livraison concrète** — Je ne fais pas que de la recherche, je produis des systèmes qui marchent, sur du hardware réel.

**Point faible (à formuler comme un axe de progression) :**
> "Je travaille souvent seul en tant qu'indépendant, donc je dois faire attention à bien documenter et communiquer quand j'intègre une équipe. C'est quelque chose que j'améliore activement — je maintiens un projet open source bien documenté et j'ai appris à structurer mon code pour qu'il soit collaboratif dès le départ."

### "Pourquoi voulez-vous travailler chez AfterQuery ?"
> "AfterQuery travaille exactement à l'intersection qui m'intéresse : les kernels GPU, l'optimisation d'inférence LLM, et les internals PyTorch. J'ai déjà des PR mergées dans ce domaine (AutoAWQ, transformers), et je veux approfondir. Ce qui me motive particulièrement, c'est de travailler sur des problèmes de bas niveau avec un impact direct sur les performances des modèles — et de le faire dans un cadre où je peux collaborer avec d'autres experts du domaine."

### "Où vous voyez-vous dans 5 ans ?"
> "Je me vois comme un expert reconnu en optimisation d'inférence LLM — capable de concevoir et d'optimiser des pipelines d'inférence complets, du kernel GPU jusqu'au déploiement en production. Que ce soit chez AfterQuery ou ailleurs, je veux être la personne qu'on appelle quand on a besoin de faire tourner un modèle plus vite, avec moins de ressources, ou sur du hardware inhabituel."

### "Parlez-nous de votre plus grande réalisation technique"
> "Mon plus grand accomplissement, c'est d'avoir conçu et fait fonctionner un assistant IA multi-agent complet sur du hardware local — 96GB RAM, dual RTX Titan. Pas de cloud, pas de GPU loué. Le système orchestre des agents spécialisés (recherche web, opérations système, édition de fichiers) via langage naturel, avec une inference LLM on-premise. C'est technique : j'ai dû optimiser les kernels CUDA (via llama.cpp), configurer le serving d'inférence, concevoir l'architecture multi-agent, et gérer les contraintes mémoire de GPU. C'est le genre de projet où je suis intervenu à tous les niveaux — du bit au bouton."

### "Quel est votre plus grand échec ?"
> "Ma première tentative de faire tourner un modèle 70B en local a échoué — je n'avais pas anticipé les contraintes mémoire des kernels MoE et le système plantait systématiquement. J'ai perdu une semaine à debugger. La leçon : j'ai appris à faire des benchmarks précis avant de concevoir l'architecture, à comprendre les profils mémoire des différents kernels, et à documenter ces contraintes. Maintenant j'ai un workflow de test systématique qui évite ce genre de surprise."

### "Quelles sont vos prétentions salariales ?"
> "Pour ce type de travail sur les kernels GPU et l'optimisation d'inférence, je vise une fourchette de $100-150/h, ce qui est cohérent avec le tier expert d'AfterQuery et les benchmarks du marché pour ce niveau de spécialisation. Mais je suis ouvert à discuter en fonction du volume et de la nature des projets."

---

## 💥 Effet WOW — Ce qui te rend unique

### WOW 1 : PR mergées dans les deux sens de la stack
> "J'ai des PR mergées dans **AutoAWQ** (kernels CUDA de quantification) ET dans **HuggingFace transformers** (internals PyTorch) ET dans **Coqui-STT** (pipelines TF/TFLite). Peu de développeurs peuvent montrer des contributions dans les trois couches — bas niveau GPU, middle level framework, et application."

### WOW 2 : Assistant IA 100% on-premise
> "Mon assistant IA multi-agent tourne sur mon hardware local — 96GB RAM, dual RTX Titan. Pas de cloud, pas de dépendance externe. C'est la preuve que je maîtrise toute la chaîne : optimisation CUDA, inference serving, architecture multi-agent, et déploiement. Si quelqu'un doit concevoir un système d'inférence optimisé pour des contraintes hardware spécifiques, j'ai déjà fait ça."

### WOW 3 : Du CFC commercial aux kernels CUDA
> "Autodidacte, je suis passé d'un CFC commercial à des PR mergées dans des kernels CUDA de quantification. Mon parcours prouve que je peux apprendre n'importe quelle techno par moi-même et produire des résultats concrets et vérifiables. Pas de bullshit, pas de théorie — du code qui marche et qui a été reviewé et accepté par les mainteneurs de projets open source majeurs."

