/**
 * 设置主页 - 重定向到个人资料
 */

import { redirect } from "next/navigation";

export default function SettingsPage() {
  redirect("/settings/profile");
}
