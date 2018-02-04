app.controller('TracksContainer', function ($scope, $http) {
    var vm = this;
    vm.params = setUpParams();
    vm.companies = {
        cellcom: 'סלקום', partner: 'פרטנר', pelephon: 'פלאפון',
        'mobile_012': '012 מובייל', hot_mobile: 'הוט מובייל', golan_telecom: 'גולן טלקום', rami_levi: 'רמי לוי'
    };
    vm.select_track = null;


    vm.post = function () {
        $http.post('/api/admin/tracks', vm.params).then(function (value) {
            console.log(value);
            vm.get();
            $('#trackPostModal').modal('toggle');
            vm.params = setUpParams();
        }, errorCallback());
    };
    vm.get = function () {
        $http.get('/api/admin/tracks').then(function (response) {
            vm.tracks = response.data;
            console.log(vm.tracks)
        }, errorCallback)
    };
    vm.delete = function () {
        $http.delete('/api/admin/tracks/' + vm.select_track.id).then(function (response) {
            vm.get();
            $('#trackDeletetModal').modal('toggle');
        }, errorCallback)
    };
    vm.put = function () {
        var id = vm.select_track.id;
        delete vm.select_track.id;
        $http.put('/api/admin/tracks/' + id, vm.select_track).then(function (response) {
            vm.get();
            $('#trackPutModal').modal('toggle');
        }, errorCallback)
    };

    function errorCallback(error) {
        console.log(error)
    }

    function setUpParams() {
        return {company: null, price: null, track_name: null, description: null, kosher: false}
    }

    vm.get();

});

