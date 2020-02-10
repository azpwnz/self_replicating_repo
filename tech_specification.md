## self_replicating_repo app

### Overview
This app allows replicating its own code into user's Github repository.


### What does it do?
The application request access to the user's Github profile and creates a repository with its own (application's) code. 
The authorization is implemented using Github OAuth app and only requires "public repo" access.

### How it works?
1. The user opens the app home page and click "Replicate" URL.
2. If the user is not authorized yet, the app will redirect the user to Github authorization page.  
3. Once the user is authorized, the app will create an empty repository and commit all app's files there on the user's behalf.  