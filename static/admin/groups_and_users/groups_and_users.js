app.controller('GAUContainer', function ($scope, $http) {
    var vm = this;
    vm.params = setUpParams();

    vm.select_user = null;
    vm.select_group = null;

    //POST--------------------------------------------------------------------------------------------------------------
    vm.post_group = function () {
        console.log(vm.params.groups);
        $http.post('/api/admin/groups', vm.params.groups).then(function (value) {
            console.log(value);
            vm.get_groups();
            $('#groupPostModal').modal('toggle');
            vm.params = setUpParams();
        }, errorCallback());
    };
    vm.post_user = function () {
        $http.post('/api/admin/tmp', vm.params.users).then(function (value) {
            console.log(value);
            vm.get_users();
            $('#userPostModal').modal('toggle');
            vm.params = setUpParams();
        }, errorCallback());
    };
    //GET---------------------------------------------------------------------------------------------------------------
    vm.get_groups = function () {
        $http.get('/api/admin/groups').then(function (response) {
            vm.groups = response.data;
            console.log(vm.groups)
        }, errorCallback)
    };
    vm.get_users = function () {
        $http.get('/api/admin/users').then(function (response) {
            vm.users = response.data;
            console.log(vm.users)
        }, errorCallback)
    };
    //DELET-------------------------------------------------------------------------------------------------------------
    vm.delete_groups = function () {
        $http.delete('/api/admin/groups/' + vm.select_group.id).then(function (response) {
            vm.get_groups();
            $('#groupDeletetModal').modal('toggle');
        }, errorCallback)
    };
    vm.delete_users = function () {
        $http.delete('/api/admin/users/' + vm.select_user.id).then(function (response) {
            vm.get_users();
            $('#userDeletetModal').modal('toggle');
        }, errorCallback)
    };
    //PUT---------------------------------------------------------------------------------------------------------------
    vm.put_groups = function () {
        var id_group = vm.select_group.id;
        delete vm.select_group.id;
        $http.put('/api/admin/groups/' + id_group, vm.select_group).then(function (response) {
            vm.get_groups();
            $('#groupPutModal').modal('toggle');
        }, errorCallback)
    };
    vm.put_users = function () {
        var id_user = vm.select_user.id;
        delete vm.select_user.id;
        $http.put('/api/admin/users/' + id_user, vm.select_user).then(function (response) {
            vm.get_users();
            $('#userPutModal').modal('toggle');
        }, errorCallback)
    };

    //OTHER-------------------------------------------------------------------------------------------------------------
    function errorCallback(error) {
        console.log(error)
    }

    function setUpParams() {

        return {
            groups: {group_name: null},
            users: {
                group_id: null,
                user_email: null,
                user_first_name: null,
                user_last_name: null,
                user_phone: null
            }
        }
    }

    vm.get_groups();
    vm.get_users();

});

