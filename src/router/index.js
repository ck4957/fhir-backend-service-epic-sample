import { createRouter, createWebHistory } from "vue-router";

const routes = [
    {
        path: "/",
        component: () => import("../components/HelloWorld.vue"),
    },
    {
        path: "/clinicians-app",
        component: () => import("../components/HelloWorld.vue"),
    }
]
const router = createRouter({
    history: createWebHistory(),
    routes,
  });
  
  export default router;
  