# Strategies of Code-switching in Human-Machine Dialogs

This repository contains the implementation and analysis code for the experiments described in our paper:

> **Strategies of Code-switching in Human-Machine Dialogs**
> [Bilingualism: Language and Cognition (2025)](https://doi.org/10.1017/S1366728925100436)

## Overview

Our project implements a **Map-Task chatbot** used to study code-switching in human–machine interactions.
It features a **client–server architecture**:

* **Client:** A React-based web application providing the interactive map-task interface for participants.
* **Server:** A Python Flask application implementing the chatbot agent logic and handling communication with the client.

In addition, the repository includes an **`analysis/`** directory containing scripts and notebooks for **post-processing and analyzing collected data** from our experiments.

## Paper Link

📄 **Published Paper:** Geckt D, Fricke M, Wintner S. [Strategies of code-switching in human–machine dialogs](https://www.cambridge.org/core/journals/bilingualism-language-and-cognition/article/strategies-of-codeswitching-in-humanmachine-dialogs/A20A85FB5A2F63D4011582C11C6B67E9?utm_campaign=shareaholic&utm_medium=copy_link&utm_source=bookmark). *Bilingualism: Language and Cognition*. Published online 2025:1-15. doi:[10.1017/S1366728925100436](https://doi.org/10.1017/S1366728925100436)
If you use this code in your work, please cite our paper:

📄 [Read the preprint on arXiv](https://arxiv.org/abs/2508.07325)


If you use this code in your work, please cite our paper:

```bibtex
@article{geckt2025strategiescodeswitchinghumanmachinedialogs,
      title={Strategies of code-switching in human-machine dialogs}, 
      author={Geckt, Dean and Fricke, Melinda and Wintner, Shuly},
      journal={Bilingualism: Language and Cognition},
      pages={1--15},
      year={2025},
      publisher={Cambridge University Press},
      doi={10.1017/S1366728925100436},
      url={https://doi.org/10.1017/S1366728925100436}
}
```

## Directory Structure

```
.
├── client/        # React web application for the Map-Task interface
├── server/        # Python Flask application implementing the chatbot
├── analysis/      # Data post-processing and analysis scripts
└── README.md
```

