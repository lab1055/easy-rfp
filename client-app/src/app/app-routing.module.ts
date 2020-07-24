import { NgModule } from "@angular/core";
import { Routes, RouterModule } from "@angular/router";
import { RealtimeComponent } from "./realtime/realtime.component";
import { SchedulerComponent } from "./scheduler/scheduler.component";

const routes: Routes = [
  {
    path: "",
    component: RealtimeComponent,
  },
  {
    path: "realtime",
    component: RealtimeComponent,
  },
  {
    path: "scheduler",
    component: SchedulerComponent,
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
