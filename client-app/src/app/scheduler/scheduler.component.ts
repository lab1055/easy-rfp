import { Component, OnInit } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { SocketioService } from "../socketio.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";

import { environment } from "../../environments/environment";

@Component({
  selector: "app-scheduler",
  templateUrl: "./scheduler.component.html",
  styleUrls: ["./scheduler.component.scss"],
})
export class SchedulerComponent implements OnInit {
  tasks = [];
  messages = [];
  form;
  submitted = false;
  constructor(
    private http: HttpClient,
    private socketService: SocketioService
  ) {}

  ngOnInit() {
    this.form = new FormGroup({
      // type: new FormControl("", Validators.required),
      task: new FormControl("", Validators.required),
      email: new FormControl("", Validators.required),
      captureInterval: new FormControl("", Validators.required),
      notifInterval: new FormControl("", Validators.required),
      totalTime: new FormControl("", Validators.required),
    });

    this.socketService.dataEventsSubject.subscribe((res) => {
      this.messages.push(res);
    });
    this.http
      .get(environment.SOCKET_ENDPOINT + "/getAllTasks")
      .subscribe((res: any) => {
        console.log("ALL TASKS", res);
        this.tasks = res;
      });
  }

  submitForSchedule() {
    this.submitted = !this.submitted;
    this.http
      .post(environment.SOCKET_ENDPOINT + "/schedule", this.form.value)
      .subscribe((res: any) => {
        if (res.success) {
          this.submitted = false;
          this.form.reset();
        }
      });
  }

  endProcess() {
    this.http.get(environment.SOCKET_ENDPOINT + "/shutdown").subscribe();
    this.socketService.socket.close();
  }
}
