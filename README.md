# Trace Route
Trace route implemented in python 3.6

## How to run

```
python TraceRoute.py [DestinationHostName]
```

## Description

Trace route works with setting the ttl in the IP protocol ttl 
is the acronym of time to live, 
every time it passes through a router, ttl will be substracted
by 1, when it become 0, it will be dropped by the router(R.I.P).

By setting the ttl from 1 to 2 and so on, we could track the
route that the packet is trasmmited through, and that is exactly how
trace route is done.

P.S. Trace route sends 3 packets per ttl rather than 1.

## Problems

1. If you are a windows user, you are likely to have windows defender 
or any other firewall, and the fire wall might block the ICMP reply, and 
thus trace route couldn't work and times out every time until it arrives
 its destination, so try shutting down your firewall if it doesn't work.



2. If you are a windows user, there might be some other problems such as 
the time is weird, getting a lot of 0.0ms, if that happen, change all time.time() 
to time.clock() in the program, I don't know why time.time() fails somtimes, 
if you know the reason, please notice me, I will be very thankful :)



3. A problem that I still don't know why it occurs:
Sometimes when sending the packet immediately after receiving it, somehow I
can't receive the packets normally, and the time becomes very weird.
If the problem occurs, just add a time.sleep() between every packet sent.

## Built With

* Python 3.6.0 :: Anaconda custom (64-bit)

## Authors

* **SaKaTetsu** - *Initial work* - [SaKaTetsu](https://github.com/SaKaTetsu)