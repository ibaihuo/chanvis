import Vue from 'vue';
// import App from './App.vue';
import App from './ChanApp.vue'
// import App from './OcnApp.vue'
import './main.css';

Vue.config.productionTip = false

new Vue({
  render: h => h(App)
}).$mount('#app')
