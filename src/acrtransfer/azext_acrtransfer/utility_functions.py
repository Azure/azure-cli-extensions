def poll_output(poller, poll_interval=10):
    print("Operation Status: " + poller.status())
    while(not poller.done()):
        print("Please wait " + str(poll_interval) + " seconds for the next update.")
        poller.wait(timeout=poll_interval)
        print("Operation Status: " + poller.status())
    return poller.status()