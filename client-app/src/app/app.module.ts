import { BrowserModule } from "@angular/platform-browser";
import { NgModule } from "@angular/core";
import { HttpClientModule } from "@angular/common/http";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { SocketioService } from "./socketio.service";
import { DashboardComponent } from "./dashboard/dashboard.component";
import { RealtimeComponent } from "./realtime/realtime.component";
import { SchedulerComponent } from "./scheduler/scheduler.component";

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    RealtimeComponent,
    SchedulerComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  providers: [SocketioService],
  bootstrap: [AppComponent],
})
export class AppModule {}
