import { Injectable } from "@angular/core";
import * as io from "socket.io-client";
import { Subject } from "rxjs";

import { environment } from "../environments/environment";

@Injectable({
  providedIn: "root",
})
export class SocketioService {
  // dataEvents$;
  dataEventsSubject = new Subject();
  socket;
  constructor() {}

  setupSocketConnection() {
    if (!this.socket) {
      this.socket = io(environment.SOCKET_ENDPOINT);
    }

    this.socket.emit("connect");

    this.socket.on("responseMessage", (res) => {
      console.log("Response message - ", res.data);
    });

    this.socket.on("Logs", (res) => {
      this.dataEventsSubject.next(res.data);
    });
  }

  getSocket() {
    return this.socket;
  }
}
