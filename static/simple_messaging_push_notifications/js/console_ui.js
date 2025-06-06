/* global moment, alert, FormData */

$(document).ready(function () {
  window.messageExtensionFunctions.push(function(formData) {
    const title = $('#field_notification_title').val()

    const positive = $('#field_response_positive').val()
    const negative = $('#field_response_negative').val()
    const neutral = $('#field_response_neutral').val()

    if (title !== '') {
        formData.append('push_notification_title', title)
    }

    if (positive !== '') {
        formData.append('push_notification_positive_option', positive)
    }

    if (negative !== '') {
        formData.append('push_notification_negative_option', negative)
    }

    if (neutral !== '') {
        formData.append('push_notification_neutral_option', neutral)
    }
  })
})
