<template>
<div class="app">
  <header class="app__header">
    <!-- <h5 class="app__title">
      QuantChan by Baihuo
    </h5> -->
  </header>
  <ChanContainer />
</div>
</template>

<script>
import ChanContainer from './components/ChanContainer.vue'
export default {
  name: 'app',
  components: {
    ChanContainer
  }
}
</script>

<style lang="scss" scoped>
.app {
    text-align: center;

    &__header {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px 0;
        background-color: #222;
        color: #fff;
    }

    &__title {
        display: block;
        font-size: 1.5em;
    }
}
</style>
