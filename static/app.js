var app = angular.module('app', ['ui.sortable']);
app.config(['$interpolateProvider', function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);
app.controller('MainController', function ($scope, $http) {
    var vm = this;

    $http.get('/api/admin/status_sale').then(function (value) {
        vm.statusSale = value.data;
    });
});

