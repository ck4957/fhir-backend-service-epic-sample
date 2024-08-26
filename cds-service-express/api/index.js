import express from 'express';
import cors from 'cors';
import bodyparse from 'body-parser';
import { handleCoverageCheck } from './crd-coverage-check.js';
import { handleOrderSignHook } from './crd-cds-hook.example.js';
import http from 'http';

const app = express();
// Configure CORS to allow requests from sandbox.cds-hooks.org
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allowedHeaders: ['authorization', 'Content-Type'],

}));

app.use(express.json());

const server = http.createServer(app);

// Define the CDS services
const cdsServices = {
    "services": [
        {
            "hook": "coverage-check",
            "title": "Coverage Check",
            "description": "Checks if the requested service is covered by the patient's insurance.",
            "prefetch": {
                "patient": "Patient/{{context.patientId}}"
            }
        },
        {
            "hook": "order-sign-hook",
            "title": "Order Sign Hook",
            "description": "Provides decision support at the time of signing an order.",
            "prefetch": {
                "patient": "Patient/{{context.patientId}}",
                "medicationOrder": "MedicationOrder?patient={{context.patientId}}"
            }
        }
    ]
}

app.get('/', (req, res) => {
    res.send('CRD service is running');
    res.setHeader("Access-Control-Allow-Origin", "*")
    res.setHeader("Access-Control-Allow-Credentials", "true");
    res.setHeader("Access-Control-Max-Age", "1800");
    res.setHeader("Access-Control-Allow-Headers", "content-type");
    res.setHeader( "Access-Control-Allow-Methods", "PUT, POST, GET, DELETE, PATCH, OPTIONS" ); 
});

// Discovery endpoint
app.get('/cds-services', (req, res)=>{
    
    res.setHeader("Access-Control-Allow-Origin", "*")
    res.setHeader("Access-Control-Allow-Credentials", "true");
    res.setHeader("Access-Control-Max-Age", "1800");
    res.setHeader("Access-Control-Allow-Headers", "content-type");
    res.setHeader( "Access-Control-Allow-Methods", "PUT, POST, GET, DELETE, PATCH, OPTIONS" ); 

    res.json(cdsServices);
});

app.post('/cds-services/coverage-check', (req, res) => {
    const hook = req.body;
    const response = handleCoverageCheck(hook);
    res.json(response);
});

// Express.js route handler for the CDS Hooks endpoint
app.post('/cds-services/order-sign-hook', (req, res) => {
    const hook = req.body;
    const response = handleOrderSignHook(hook);
    res.json(response);
});

const port = 3000;

app.listen(port, () => {
    console.log(`CRD service listening at http://localhost:${port}`);
});
