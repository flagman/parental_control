<template>
  <b-container>
    <b-row class="mt-5" align-h="center" align-v="baseline">
      <b-col col lg="1">
        <b-avatar variant="info" src="misha.jpg"></b-avatar>
      </b-col>
      <b-col col lg="1" v-if="parentalControl">
        <b-form-checkbox
          v-model="internetEnabled"
          @change="toggleInternet"
          name="check-button"
          switch
        ></b-form-checkbox>
      </b-col>
      <b-col col lg="2" v-if="parentalControl">
        <b-form-input :value="timeLeft" disabled></b-form-input>
      </b-col>
      <b-col col lg="4" v-if="!parentalControl">
        <b-form-input disabled placeholder="Контроль интернета отключен"></b-form-input>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
// @ is an alias to /src
// import HelloWorld from "@/components/HelloWorld.vue";
import axios from "axios";

const transport = axios.create({
  withCredentials: true,
  baseURL: "http://192.168.31.122/api"
});

function convertTime(sec) {
  var hours = Math.floor(sec / 3600);
  hours >= 1 ? (sec = sec - hours * 3600) : (hours = "00");
  var min = Math.floor(sec / 60);
  min >= 1 ? (sec = sec - min * 60) : (min = "00");
  sec < 1 ? (sec = "00") : void 0;

  min.toString().length == 1 ? (min = "0" + min) : void 0;
  sec.toString().length == 1 ? (sec = "0" + sec) : void 0;

  return hours + ":" + min + ":" + sec;
}

export default {
  name: "Child",
  data: () => {
    return {
      time: 0,
      internetEnabled: false,
      parentalControl: false,
      intervalHandle: null,
      allowedDailyLimit: 0
    };
  },
  mounted() {
    this.getStatus();
    this.intervalHandle = setInterval(() => {
      this.getStatus();
    }, 5000);
  },
  beforeDestroy() {
    clearInterval(this.intervalHandle);
  },
  methods: {
    getStatus() {
      transport.get("/status").then(response => {
        this.time = response.data.daily_time_spent;
        this.internetEnabled = response.data.internet_on;
        this.parentalControl = response.data.parent_control;
        this.allowedDailyLimit = response.data.allowed_time_daily * 60;
      });
    },
    toggleInternet(state) {
      transport
        .put("/internet", {}, { params: { state: state.toString() } })
        .then(() => {
          this.getStatus();
        });
    }
  },
  computed: {
    timeLeft() {
      return convertTime(Math.floor(this.allowedDailyLimit - this.time));
    }
  },
  components: {
    // TopMenu
    // HelloWorld
  }
};
</script>
