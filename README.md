# FHIR Backend Service Epic Sample

This project is a sample implementation of a FHIR (Fast Healthcare Interoperability Resources) backend service using the Epic EHR system.

## Installation

To install this project, follow these steps:

```bash
git clone https://github.com/username/fhir-backend-service-epic-sample.git
cd fhir-backend-service-epic-sample
npm install
```

## Steps to Run App Locally

1. Register a clinician facing app on Epic FHIR portal:
    - Redirect Uri: `https://localhost:8000/clinicians-app`
    - Non-Prod Client Id: `<Get the value from Epic App>`

2. Run the Vue App:
    ```bash
    npm run dev
    ```

3. Navigate to `localhost:8000`:
    - Click `Sign In`
    - You will be redirected to the Epic Login Screen. Use the following credentials:
        - Username: `FHIR`
        - Password: `EpicFhir11!`
    - Reference: [Epic FHIR Test Patients](https://fhir.epic.com/Documentation?docId=testpatients)

4. You will be redirected back to `https://localhost:8000/clinicians-app?code=<code>`. Reload the same URL again by removing 's' from `https`.


## API Documentation
This project adheres to the FHIR standard for healthcare data exchange. For more details about the API endpoints and request/response formats, please refer to the official FHIR documentation.

## Contributing
Contributions are welcome. Please follow these steps to contribute:


1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request


## License
This project is licensed under the MIT License. See LICENSE for more information.


Project Link: https://github.com/your_username/fhir-backend-service-epic-sample

```
