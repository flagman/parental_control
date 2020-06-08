<template>
  <b-container>
    <top-menu></top-menu>
    <component :is="appropriateComponent"></component>
  </b-container>
</template>

<script>
// @ is an alias to /src
// import HelloWorld from "@/components/HelloWorld.vue";

import TopMenu from "@/components/menu.vue";

export default {
  name: "Home",
  components: {
    TopMenu,
    Child: () => import("@/views/Child.vue"),
    Parent: () => import("@/views/Parent.vue")
  },
  computed: {
    appropriateComponent() {
      return this.$cookies.get("auth") == "parent" ? "Parent" : "Child";
    }
  }
};
</script>
