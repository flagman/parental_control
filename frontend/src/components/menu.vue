<template>
  <b-container>
    <b-button variant="primary" size="sm" @click="logout">Выйти</b-button>
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

export default {
  name: "TopMenu",
  methods: {
    logout() {
      transport.post("/logout").then(response => {
        if (response.data.code == 0) {
          this.$router.push({ path: "/login" });
        }
      });
    }
  }
};
</script>
