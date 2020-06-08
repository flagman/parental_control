<template>
  <b-container>
    <b-form @submit="onSubmit">
      <b-form-group
        id="input-group-1"
        label="Пароль:"
        label-for="input-1"
        description="Кто забыл, тот без инета :))"
      >
        <b-form-input id="input-1" v-model="password" type="password" required placeholder></b-form-input>
      </b-form-group>
      <b-button type="submit" variant="primary" v-if="!working">Вход</b-button>
      <b-spinner variant="primary" label="Spinning" v-else></b-spinner>
    </b-form>
  </b-container>
</template>

<script>
// @ is an alias to /src
import axios from "axios";

const transport = axios.create({
  withCredentials: true,
  baseURL: "http://192.168.31.122/api"
});

export default {
  data() {
    return {
      password: "",
      working: false
    };
  },

  methods: {
    onSubmit(evt) {
      evt.preventDefault();
      this.working = true;
      transport
        .post("/login", null, {
          params: { password: this.password }
        })
        .then(response => {
          this.working = false;
          if (response.data.code == 0) {
            this.$router.push({ path: "/" });
          }
        });
    }
  }
};
</script>
