"use strict"
// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function getCookie(name) {
    'use strict';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function setParametro(cve_parametro, valor) {
    'use strict';
    const parameters = {"action": "SetParametro", "cve_parametro": cve_parametro, "valor": valor}
    _ajax('/parametros/', parameters, function () {
    })
}

function UnblockUI_(){
    'use strict';
    $('.wrapper').unblock();
}

function blockUI_(){
    'use strict';
      $('.wrapper').block({
                message: '<img width="90" height="79" src="/static/sismbor/img/loading.gif" />',
                overlayCSS: { backgroundColor: '#fff',opacity: 1 },
                css: {
                    border: 'none',
                    opacity: 1,
                    color: '#fff'
                }
            });
}
// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function fajax(parameters, callback) {
    'use strict';
    var url = window.location.pathname;
    $.ajax({
        url: url,
        type: 'POST',
        beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        data: parameters,
        dataType: 'json'
    }).done(function (data) {

        if (!data.hasOwnProperty('error')) {
            if (data.hasOwnProperty('msgInfo')) {
                message_info(data.msgInfo, callback, data);
                return false;
            }

            if (data.hasOwnProperty('msgConfirmar')) {

                message_info(data.msgConfirmar, function (data) {


                    parameters.set("confirmado", true);

                    _ajax(url, parameters, callback(data));
                }, data);
                return false;
            }

            if (data.hasOwnProperty('psCOD_RESP')) {
                if (parseInt(data.psCOD_RESP) == 0 ) {
                    callback(data);
                    return false;
                } else {
                    message_error(data.psSTR_RESP);
                    return false;
                }
            }

            callback(data);
            return false;
        }

        if (data['error'].indexOf('1062') == 1) {
            message_error('Registro duplicado ' + data['info_datos']);
        } else {
            message_error(data.error);
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {


    });
}// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function lajax(parameters, callback) {
    'use strict';
    var url = window.location.pathname;
    $.ajax({
        url: url,
        type: 'POST',
        data: parameters,
        dataType: 'json'
    }).done(function (data) {

        if (!data.hasOwnProperty('error')) {
            if (data.hasOwnProperty('msgInfo')) {
                message_info(data.msgInfo, callback, data);
                return false;
            }

            if (data.hasOwnProperty('msgConfirmar')) {

                message_info(data.msgConfirmar, function (data) {


                    parameters.set("confirmado", true);

                    _ajax(url, parameters, callback(data));
                }, data);
                return false;
            }

            if (data.hasOwnProperty('psCOD_RESP')) {
                if (parseInt(data.psCOD_RESP) == 0 ) {
                    callback(data);
                    return false;
                } else {
                    message_error(data.psSTR_RESP);
                    return false;
                }
            }

            callback(data);
            return false;
        }

        if (data['error'].indexOf('1062') == 1) {
            message_error('Registro duplicado ' + data['info_datos']);
        } else {
            message_error(data.error);
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {


    });
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function _ajax(url, parameters, callback) {
    'use strict';
    // if (bEsDemo) {
    //     message_error('Cuenta demo. Solo lectura');
    // } else {
    $.ajax({
        url: url, //window.location.pathname
        type: 'POST',
        beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        data: parameters,
        dataType: 'json'
        // processData: false,
        // contentType: false,
    }).done(function (data) {

        if (!data.hasOwnProperty('error')) {
            if (data.hasOwnProperty('msgInfo')) {
                message_info(data.msgInfo, callback, data);
                return false;
            }

            if (data.hasOwnProperty('msgConfirmar')) {

                message_info(data.msgConfirmar, function (data) {


                    parameters.set("confirmado", true);

                    _ajax(url, parameters, callback(data));
                }, data);
                return false;
            }

            if (data.hasOwnProperty('psCOD_RESP')) {
                if (parseInt(data.psCOD_RESP) == 0 ) {
                    callback(data);
                    return false;
                } else {
                    message_error(data.psSTR_RESP);
                    return false;
                }
            }

            callback(data);
            return false;
        }

        if (data['error'].indexOf('1062') == 1) {
            message_error('Registro duplicado ' + data['info_datos']);
        } else {
            message_error(data.error);
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (data) {


    });

    // }

}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function submit_(url, title, content, parameters, callback) {
    'use strict';
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'large',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        data: parameters,
                        dataType: 'json',
                        processData: false,
                        contentType: false,
                    }).done(function (data) {
                        if (!data.hasOwnProperty('error')) {
                            if (data.hasOwnProperty('msgInfo')) {

                                message_info(data.msgInfo, callback, data);
                                return false;
                            }

                            if (data.hasOwnProperty('msgArchivoCargado')) {
                                message_info(data.msgArchivoCargado, function (data) {
                                    parameters.set("sobreescribir", true);
                                    submit_(window.location.pathname, 'Notificación', '¿Sobre escribir carga anterior? ', parameters, function (data) {
                                        location.href = '/';
                                    });
                                }, data);
                                return false;
                            }
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);
                    }).always(function (data) {

                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function ajax_confirm(url, title, content, parameters, callback, Infotext) {
    'use strict';
    if (Infotext !== undefined ){
        var vInfotext = Infotext

    }else{
        var vInfotext
    }


    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: vInfotext,
                btnClass: 'btn-primary',
                action: function () {
                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        data: parameters,
                        // dataType: 'json',
                        // processData: false,
                        // contentType: false,
                    }).done(function (data) {
                        if (!data.hasOwnProperty('error')) {
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);
                    }).always(function (data) {

                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function message_info(obj, callback, data) {
    'use strict';
    var html = '';
    if (typeof (obj) === 'object') {
        html = '<ul style="text-align: left;">';
        $.each(obj, function (key, value) {
            html += '<li>' + key + ': ' + value + '</li>';
        });
        html += '</ul>';
    } else {
        html = '<p>' + obj + '</p>';
    }
    Swal.fire({
        title: 'Aviso!',
        html: html,
        icon: 'info',
        confirmButtonText: 'Aceptar',
        allowOutsideClick: false
    }).then(function (result) {
        if (callback != null)
            callback(data);
    });
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function message_error(obj) {
    'use strict';
    var html = '';
    if (typeof (obj) === 'object') {
        html = '<ul style="text-align: left;">';
        $.each(obj, function (key, value) {
            html += '<li>' + key + ': ' + value + '</li>';
        });
        html += '</ul>';
    } else {
        html = '<p>' + obj + '</p>';
    }
    Swal.fire({
        title: 'Error!',
        html: html,
        icon: 'error'
    });

}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function message_error_callback(obj, callback) {
    'use strict';
    var html = '';
    if (typeof (obj) === 'object') {
        html = '<ul style="text-align: left;">';
        $.each(obj, function (key, value) {
            html += '<li>' + key + ': ' + value + '</li>';
        });
        html += '</ul>';
    } else {
        html = '<p>' + obj + '</p>';
    }
    Swal.fire({
        title: 'Error!',
        html: html,
        icon: 'error'
    }).then(function (result) {
        callback(result)
    });

}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function confirmar_accion(title, content, callback) {
    'use strict';
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    callback();
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {
                    // cancel();
                }
            },
        }
    })
}

function ajax_reload(TableName) {
    'use strict';
    $(TableName).DataTable().ajax.reload(null, false);
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #


function submit_with_ajax_catalogos(url, title, content, parameters, callback) {
    'use strict';
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        data: parameters,
                        dataType: 'json',
                        processData: false,
                        contentType: false,
                    }).done(function (data) {

                        if (!data.hasOwnProperty('error')) {
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);
                    }).always(function (data) {

                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #


function submit_with_ajax_fotos(url, title, content, parameters, callback) {
    'use strict';
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {

                    document.getElementById("loadingDiv").style.display = 'block';
                    $('#loadingDiv').show();
                    window.scrollTo(0,0);

                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        data: parameters,
                        dataType: 'json',
                        processData: false,
                        contentType: false,
                    }).done(function (data) {

                        if (!data.hasOwnProperty('error')) {
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);

                    }).always(function (data) {
                        document.getElementById("loadingDiv").style.display = 'none';
                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #

function submit_with_ajax(url, title, content, parameters, callback) {
    'use strict';
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        data: parameters,
                        dataType: 'json',
                        dataSrc: "",
                        processData: false
                    }).done(function (data) {

                        if (!data.hasOwnProperty('error')) {
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);
                    }).always(function (data) {

                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
}

// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #
function submit_with_ajax_action(parameters, callback) {
    'use strict';
    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        beforeSend: function (request) {
            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        },
        data: parameters,
        dataType: 'json',
        dataSrc: "",
        // processData: false
    }).done(function (response) {

        if (!response.hasOwnProperty('error')) {
            callback(response);
            return false;
        }
        message_error(response.error);
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(textStatus + ': ' + errorThrown);
    }).always(function (response) {

    });

}


// # ***************************************************************************************************************** #
// # ***************************************************************************************************************** #

function submit_with_ajax_json(url, title, content, parameters, callback) {
    'use strict';
    $.confirm({
        theme: 'material',
        title: title,
        icon: 'fa fa-info',
        content: content,
        columnClass: 'small',
        typeAnimated: true,
        cancelButtonClass: 'btn-primary',
        draggable: true,
        dragWindowBorder: false,
        buttons: {
            info: {
                text: "Si",
                btnClass: 'btn-primary',
                action: function () {
                    $.ajax({
                        url: url, //window.location.pathname
                        type: 'POST',
                        beforeSend: function (request) {
                            request.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        },
                        data: parameters,
                        dataType: 'json',
                        processData: true
                    }).done(function (data) {

                        if (!data.hasOwnProperty('error')) {
                            callback(data);
                            return false;
                        }
                        message_error(data.error);
                    }).fail(function (jqXHR, textStatus, errorThrown) {
                        alert(textStatus + ': ' + errorThrown);
                    }).always(function (data) {

                    });
                }
            },
            danger: {
                text: "No",
                btnClass: 'btn-red',
                action: function () {

                }
            },
        }
    })
}


function log(message){ console.log(message)}

function esEntero(numero){
    return (numero % 1 == 0);
}