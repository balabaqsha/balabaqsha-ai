
import os
from google.auth import default

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/bekabigeldigmail.com/PycharmProjects/Data-Extraction-from-Invoice-Images  /new_edited/key.json"

creds, project = default()
print(creds)
print(project)
