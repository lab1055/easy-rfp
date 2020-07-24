import { Component, OnInit } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { SocketioService } from "../socketio.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";

import { environment } from "../../environments/environment";

@Component({
  selector: "app-realtime",
  templateUrl: "./realtime.component.html",
  styleUrls: ["./realtime.component.scss"],
})
export class RealtimeComponent implements OnInit {
  messages = [];
  tasks = [];
  form;
  imageUrl;
  showImage = false;
  constructor(
    private http: HttpClient,
    private socketService: SocketioService
  ) {}

  ngOnInit() {
    this.form = new FormGroup({
      task: new FormControl("", Validators.required),
      email: new FormControl("", Validators.email),
    });

    this.http
      .get(environment.SOCKET_ENDPOINT + "/getAllTasks")
      .subscribe((res: any) => {
        console.log("ALL TASKS", res);
        this.tasks = res;
      });
    this.socketService.dataEventsSubject.subscribe((res) => {
      this.messages.push(res);
      setTimeout(() => {
        this.showImage = true;
      }, 3000);
    });
  }

  captureRealtime() {
    this.http
      .post(environment.SOCKET_ENDPOINT + "/realtime", this.form.value, {
        responseType: "text",
        headers: {
          "Content-Type": "text/plain",
        },
      })
      .subscribe((res) => {
        let url;
        // let blobbImg = new Blob([res], { type: "image/png" });

        // let reader = new FileReader();
        // reader.readAsDataURL(blobbImg); // converts the blob to base64 and calls onload

        // reader.onload = () => {
        //   url = reader.result; // data url
        //   console.log("URL INSIDE - ", url);
        this.imageUrl = res;
        // link.click();
        // };
        // let imageTemp;
        // const reader = new FileReader();
        // reader.onload = (e: any) => (imageTemp = e.target.result);
        // reader.readAsDataURL(new Blob([res]));

        // this.imageUrl = this.sanitizer.bypassSecurityTrustUrl(
        //   "data:image/png;base64," + imageTemp
        // );
        // console.log("IMAGE - ", res);

        // let mySrc;
        // const reader = new FileReader();
        // reader.readAsDataURL(res);
        // reader.onloadend = function () {
        //   // result includes identifier 'data:image/png;base64,' plus the base64 data
        //   mySrc = reader.result;
        // };

        // console.log(mySrc);
        // setTimeout(() => {
        //   this.imageUrl = this.sanitizer.bypassSecurityTrustResourceUrl(mySrc);
        // }, 500);
      });

    // this.http
    //   .post("http://localhost:5000/realtime", this.form.value)
    //   .subscribe((res: any) => {
    //     // console.log(res.toString());
    //     // this.imageUrl = res;

    //   });
  }
}
