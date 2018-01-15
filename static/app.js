var app = angular.module('app', ['ui.sortable']);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);
