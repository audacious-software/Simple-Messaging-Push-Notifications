self.addEventListener('notificationclick', function(event) {
  if (event.notification.data) {
    const payload = event.notification.data

    const replyUrl = payload.report_url
    const replyReporter = payload.report_reporter
    const replyRepondingTo = payload.report_responding_to

    if (replyUrl && replyReporter && replyRepondingTo) {
      let reply = ''

      if (event.action === 'positive') {
        reply = payload.include_positive_response
      } else if (event.action === 'negative') {
        reply = payload.include_negative_response
      } else if (event.action === 'neutral') {
        reply = payload.include_ok_response
      }

      if (reply !== '') {
        event.preventDefault()

        fetch("{% url 'simple_messaging_push_reply' %}", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                platform: "web",
                identifier: replyReporter,
                responding_to: replyRepondingTo,
                response: reply
            })
        }).then(function(response) {
          event.notification.close();
        })

        return
      }
    }

    const openUrl = payload.url

    if (openUrl) {
      event.waitUntil(this.self.clients.matchAll({ type: "window" }).then((clientsArr) => {
        const windowToFocus = clientsArr.find((windowClient) => windowClient.url === openUrl)

        if (windowToFocus) {
          windowToFocus.focus()
        } else {
          clients.openWindow(openUrl)
            .then((windowClient) => (windowClient ? windowClient.focus() : null))
        }

      }))
    }
  }
})

self.addEventListener('push', function(event) {
  if (event.data) {
    const payload = JSON.parse(event.data.text())

    let actions = []

    if (payload.include_positive_response !== undefined) {
      actions.push({
        title: payload.include_positive_response,
        action: 'positive'
      })
    }

    if (payload.include_negative_response !== undefined) {
      actions.push({
        title: payload.include_negative_response,
        action: 'negative'
      })
    }

    if (payload.include_ok_response !== undefined) {
      actions.push({
        title: payload.include_ok_response,
        action: 'neutral'
      })
    }

    return self.registration.showNotification(payload.title, {
      body: payload.message,
      actions,
      data: payload
      //   icon: icon,
    })
  }
})
