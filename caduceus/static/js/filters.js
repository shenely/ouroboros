<<<<<<< HEAD
=======
angular.module('kepler.filters', []).
  filter('interpolate', ['version', function(version) {
    return function(text) {
      return String(text).replace(/\%VERSION\%/mg, version);
    }
  }]);
>>>>>>> branch 'master' of https://github.com/shenely/ouroboros.git
