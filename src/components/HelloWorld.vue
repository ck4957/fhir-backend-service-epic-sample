<template>
  <!-- <h1>{{ msg }}</h1> -->
  <div class="container">
    <div style="text-align: center">
      <h1>Smart on FHIR - Patient Info</h1>
      <p><strong>Username:</strong> fhircamila</p>
      <p><strong>Password:</strong> epicepic1</p>
      <a class="btn btn-info" v-if="code == undefined" style="text-decoration: none" target="_blank"
        :href="authorizeLink">
        Sign in
      </a>
      <hr />
    </div>
    <div>
      Code:
      <pre v-if="code">{{ code }}</pre>
      Access Token:
      <pre v-if="accesstoken">{{ accesstoken }}</pre>

    </div>
    <div v-if="tokenResponse">
      <pre>{{ tokenResponse }}</pre>
    </div>
    <div v-if="accesstoken && patientdata">
      <button onclick="getPatientData()">Get Patient Data</button>
      <p><strong>Patient Id:</strong> {{ patient }}</p>

      <strong>Name: </strong>{{ patientdata.name[0].text }}<br />
      <strong>Birth Date: </strong>{{ patientdata.birthDate }} <br />
      <strong>Gender: </strong>{{ patientdata.gender }} <br />
      <strong>Vital Status: </strong>{{ patientdata.deceasedBoolean ? "Dead" : "Alive" }} <br />
      <strong>Marital Status: </strong>{{ patientdata.maritalStatus.text }}
      <br />
      <strong>Telecom: </strong> <br />
      <div v-for="telecom in patientdata.telecom" :key="telecom.value">
        <div class="ml-2">
          <strong>{{ telecom.system }}</strong> -
          {{ telecom.use }}
          {{ telecom.value }}
        </div>
      </div>

      <strong>Address: </strong> <br />
      <div v-for="address in patientdata.address" :key="address.use">
        <div class="ml-2">
          <strong>{{ address.use }} -</strong>
          {{ address.line.toString() }}, {{ address.city }},
          {{ address.district }}, {{ address.state }}, {{ address.postalCode }},
          {{ address.country }}
          <span v-if="address.period?.start"><strong>From</strong></span>
          {{ address.period?.start }}
        </div>
      </div>

      <strong>Language: </strong>{{ patientdata.communication[0].language.coding[0].display }} <br />

      <strong>General Practitioner </strong>{{ patientdata.generalPractitioner[0].display }}<br />
      <strong>Managing Organization </strong>{{ patientdata.managingOrganization.display }}<br />
      <hr />
      <strong>Access code:</strong>
      <p class="ml-2" style="word-break: break-all">{{ accesstoken }}</p>
      <strong>Patient Resource:</strong>
      <pre>{{ patientdata }}</pre>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      code: "",
      accesstoken: "",
      patient: "erXuFYUfucBZaryVksYEcMg3",
      patientdata: {},
      clientId: "df49e0d3-208d-4293-a213-4990da77013d", // Replace with your client id
      redirect: import.meta.env.PROD
        ? "https://lucid-wozniak-940eae.netlify.app"
        : "https://localhost:8000/clinicians-app/",
      tokenResponse: "",
    };
  },
  computed: {
    authorizeLink() {
      return `https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize?response_type=code&redirect_uri=${this.redirect}&client_id=${this.clientId}&state=1234&scope=patient.read`;
    },
  },
  async mounted() {
    console.log(this.$route.query.code);
    this.code = this.$route.query.code;
    if (this.code != undefined) {
      const params = new URLSearchParams();
      params.append("grant_type", "authorization_code");
      params.append("redirect_uri", this.redirect);
      params.append("code", this.code);
      params.append("client_id", this.clientId);
      params.append("state", "1234");
      const config = {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      };

      if (this.accesstoken == "") {
        this.accesstoken = localStorage.getItem('accesstoken');
        if (this.accesstoken == "") {
          alert("No access token Found");
          await axios
            .post(
              "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
              params,
              config
            )
            .then((response) => {
              console.log(response.data);
              this.tokenResponse = response.data;
              localStorage.setItem("tokenResponse", response.data);
              this.accesstoken = response.data.access_token;
              localStorage.setItem("accesstoken", this.accesstoken);
              this.patient = response.data.patient;

            })
            .catch(function (error) {
              console.log(error);
            });
        } else {
          await axios
            .get(
              `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/${this.patient}`,
              {
                headers: {
                  Authorization: `Bearer ${this.accesstoken}`,
                  Accept: 'application/json'
                }
              }
            )
            .then((response) => {
              this.patientdata = response.data;
              console.log(response);
            })
            .catch((error) => {
              console.log(error);
            });
        }
      }
    }
  },

  async getPatientData() {
    await axios
      .get(
        `https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/${this.patient}`,
        {
          headers: {
            Authorization: `Bearer ${this.accesstoken}`,
            Accept: 'application/json'
          }
        }
      )
      .then((response) => {
        this.patientdata = response.data;
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });
  }
};
// const state = reactive({ count: 0 })
</script>

<style scoped>
/* a {
  color: #42b983;
} */
</style>
