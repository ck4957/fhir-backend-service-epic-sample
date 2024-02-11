# fhir-backend-service-epic-sample

Steps to run app locally:
1. Registered a clinician facing app on Epic FHIR portal
    a. Redirect Uri: https://localhost:8000/clinicians-app
    b. Non-Prod Client Id: <Get the value from Epic App>
2. Run the Vue App
   
    `npm run dev`
4. Go to localhost:8000
   
    a. Click Sign In
   
    b. Epic Login Screen
    
        Username: FHIR
        Password: EpicFhir11!
   
        Reference: https://fhir.epic.com/Documentation?docId=testpatients
6. Redirect back to https://localhost:8000/clinicians-app?code=<code>

    a. Reload same url again by removing 's' from https
