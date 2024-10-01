This is a Python (Flask) server implementing the Map-Task bot. The entry is main.py.
it includes the implementation of the bot as well as the code-switching (CS) strategies.

Prerequisites:
- OpenAI subscription (bots/openai_util.py) in order to use API calls
- Google cloud subscription (google_cloud/) in order to use both Translation services (used only in the Alternation CS strategies) and Storage services (to store JSON output files of an experiment).
- Local models: the bot uses **Spacy** and **Transformers** (via hugging face). The models should be downloaded in advance, and stored under models/. This is because we choose to deploy the entire application with a docker image containing the models as part of its image.

    models:
    - [spaeng-lid-lince](https://huggingface.co/sagorsarker/codeswitch-spaeng-lid-lince)
    - [en_core_web_sm-3.7.1](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.7.1)
    - [es_core_news_md-3.7.0](https://github.com/explosion/spacy-models/releases/tag/es_core_news_md-3.7.0)



Previous (and currently unused) attempts and ideas of this study are also included such as the **Rule-Based** bot (prior to using GPT we implemented the bot based on regex matching and templates rules), and a **human-to-human** server (i.e., to support a study where two humans engage online without any bot).


To deploy the app we use docker image, and one might use google cloud as suggested [here](https://cloud.google.com/run/docs/deploying) and [here](https://medium.com/@taylorhughes/how-to-deploy-an-existing-docker-container-project-to-google-cloud-run-with-the-minimum-amount-of-daca0b5978d8).
