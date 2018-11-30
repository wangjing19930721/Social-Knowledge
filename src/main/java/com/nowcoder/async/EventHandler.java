package com.nowcoder.async;


public interface EventHandler {
    void doHandle(EventModel model);

    List<EventType> getSupportEventTypes();
}
