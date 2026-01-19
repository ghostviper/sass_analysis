/**
 * 偏好设置页面
 */

"use client";

import { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { useLocale } from "@/contexts/LocaleContext";
import { Card } from "@/components/ui/Card";
import { Globe, Moon, Sun, Monitor, Check, Bell, Mail, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { getUserPreference, saveUserPreference } from "@/lib/api/discover";
import type { UserPreference } from "@/types/discover";

const languages = [
  { code: "zh-CN", name: "简体中文", flag: "🇨🇳" },
  { code: "en", name: "English", flag: "🇺🇸" },
];

const themes = [
  { value: "light", name: "浅色", icon: Sun, desc: "明亮的界面" },
  { value: "dark", name: "深色", icon: Moon, desc: "护眼模式" },
  { value: "system", name: "跟随系统", icon: Monitor, desc: "自动切换" },
];

export default function PreferencesSettingsPage() {
  const { theme, setTheme } = useTheme();
  const { locale, setLocale } = useLocale();
  const { user, isAuthenticated, redirectToLogin } = useAuth();
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [marketingEmails, setMarketingEmails] = useState(false);
  const [prefLoading, setPrefLoading] = useState(false);
  const [prefSaving, setPrefSaving] = useState(false);
  const [preference, setPreference] = useState<UserPreference | null>(null);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [skillLevel, setSkillLevel] = useState<string>("beginner");

  const isEn = locale === "en";

  const roleOptions = [
    { value: "cautious_indie_dev", zh: "谨慎的独立开发者", en: "Cautious Indie Dev" },
    { value: "quick_starter", zh: "快速启动者", en: "Quick Starter" },
    { value: "opportunity_hunter", zh: "机会嗅觉型", en: "Opportunity Hunter" },
    { value: "product_driven_fan", zh: "产品驱动爱好者", en: "Product-Driven" },
    { value: "niche_hunter", zh: "细分市场猎手", en: "Niche Hunter" },
  ];

  const categoryOptions = [
    "Developer Tools",
    "API",
    "Productivity",
    "Marketing",
    "Social Media",
    "AI",
    "SaaS",
    "Business",
  ];

  const skillOptions = [
    { value: "beginner", zh: "入门", en: "Beginner" },
    { value: "intermediate", zh: "进阶", en: "Intermediate" },
    { value: "advanced", zh: "高级", en: "Advanced" },
  ];

  useEffect(() => {
    async function fetchPreference() {
      if (!user?.id) {
        setPreference(null);
        return;
      }
      try {
        setPrefLoading(true);
        const data = await getUserPreference(user.id);
        setPreference(data.preference);
        setSelectedRoles(data.preference?.preferred_roles || []);
        setSelectedCategories(data.preference?.interested_categories || []);
        setSkillLevel(data.preference?.skill_level || "beginner");
      } catch (err) {
        console.error("Failed to fetch user preference:", err);
      } finally {
        setPrefLoading(false);
      }
    }
    fetchPreference();
  }, [user?.id]);

  const toggleValue = (value: string, list: string[], setter: (next: string[]) => void) => {
    if (list.includes(value)) {
      setter(list.filter((item) => item !== value));
      return;
    }
    setter([...list, value]);
  };

  const handleSavePreference = async () => {
    if (!user?.id) {
      redirectToLogin("/settings/preferences");
      return;
    }
    try {
      setPrefSaving(true);
      const payload: Partial<UserPreference> = {
        preferred_roles: selectedRoles,
        interested_categories: selectedCategories,
        skill_level: skillLevel,
      };
      const data = await saveUserPreference(user.id, payload);
      setPreference(data.preference);
    } catch (err) {
      console.error("Failed to save preference:", err);
    } finally {
      setPrefSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 语言设置 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
            <Globe className="h-5 w-5 text-brand-500" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              语言
            </h2>
            <p className="text-sm text-content-muted">
              选择您偏好的界面语言
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLocale(lang.code as "zh-CN" | "en")}
              className={cn(
                "flex items-center gap-3 p-4 rounded-xl border transition-all duration-200",
                locale === lang.code
                  ? "border-brand-500 bg-brand-500/5"
                  : "border-surface-border hover:border-brand-500/30 hover:bg-surface/50"
              )}
            >
              <span className="text-2xl">{lang.flag}</span>
              <span className="text-sm font-medium text-content-primary flex-1 text-left">
                {lang.name}
              </span>
              {locale === lang.code && (
                <div className="h-5 w-5 rounded-full bg-brand-500 flex items-center justify-center">
                  <Check className="h-3 w-3 text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* 策展偏好 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
            <SlidersHorizontal className="h-5 w-5 text-violet-500" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              {isEn ? "Curation Preferences" : "策展偏好"}
            </h2>
            <p className="text-sm text-content-muted">
              {isEn ? "Tune what you want to explore" : "调整你想看到的推荐方向"}
            </p>
          </div>
        </div>

        {!isAuthenticated ? (
          <div className="text-sm text-content-muted">
            {isEn ? "Please sign in to save your preferences." : "请登录后保存你的偏好。"}
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <div className="text-xs text-content-muted mb-2">
                {isEn ? "Preferred roles" : "角色偏好"}
              </div>
              <div className="flex flex-wrap gap-2">
                {roleOptions.map((option) => {
                  const active = selectedRoles.includes(option.value);
                  return (
                    <button
                      key={option.value}
                      onClick={() => toggleValue(option.value, selectedRoles, setSelectedRoles)}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors",
                        active
                          ? "bg-brand-500/10 text-brand-600 border-brand-500/30"
                          : "bg-surface text-content-secondary border-surface-border hover:border-brand-500/30"
                      )}
                    >
                      {isEn ? option.en : option.zh}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <div className="text-xs text-content-muted mb-2">
                {isEn ? "Interested categories" : "关注领域"}
              </div>
              <div className="flex flex-wrap gap-2">
                {categoryOptions.map((option) => {
                  const active = selectedCategories.includes(option);
                  return (
                    <button
                      key={option}
                      onClick={() => toggleValue(option, selectedCategories, setSelectedCategories)}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors",
                        active
                          ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/30"
                          : "bg-surface text-content-secondary border-surface-border hover:border-emerald-500/30"
                      )}
                    >
                      {option}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <div className="text-xs text-content-muted mb-2">
                {isEn ? "Skill level" : "技能阶段"}
              </div>
              <div className="flex flex-wrap gap-2">
                {skillOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setSkillLevel(option.value)}
                    className={cn(
                      "px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors",
                      skillLevel === option.value
                        ? "bg-violet-500/10 text-violet-600 border-violet-500/30"
                        : "bg-surface text-content-secondary border-surface-border hover:border-violet-500/30"
                    )}
                  >
                    {isEn ? option.en : option.zh}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="text-xs text-content-muted">
                {prefLoading
                  ? (isEn ? "Loading preference..." : "加载偏好中...")
                  : preference
                    ? (isEn ? "Preference saved" : "偏好已保存")
                    : (isEn ? "No preference yet" : "尚未保存偏好")}
              </div>
              <button
                onClick={handleSavePreference}
                disabled={prefSaving}
                className={cn(
                  "px-4 py-2 rounded-lg text-xs font-medium transition-colors",
                  prefSaving
                    ? "bg-brand-500/20 text-brand-400 cursor-not-allowed"
                    : "bg-brand-500 text-white hover:bg-brand-600"
                )}
              >
                {prefSaving ? (isEn ? "Saving..." : "保存中...") : (isEn ? "Save preference" : "保存偏好")}
              </button>
            </div>
          </div>
        )}
      </Card>

      {/* 主题设置 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
            <Sun className="h-5 w-5 text-accent-secondary" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              主题
            </h2>
            <p className="text-sm text-content-muted">
              选择您偏好的界面主题
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {themes.map((t) => (
            <button
              key={t.value}
              onClick={() => setTheme(t.value)}
              className={cn(
                "flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-200",
                theme === t.value
                  ? "border-brand-500 bg-brand-500/5"
                  : "border-surface-border hover:border-brand-500/30 hover:bg-surface/50"
              )}
            >
              <div className={cn(
                "h-12 w-12 rounded-xl flex items-center justify-center",
                theme === t.value
                  ? "bg-brand-500/10"
                  : "bg-surface"
              )}>
                <t.icon
                  className={cn(
                    "h-6 w-6",
                    theme === t.value
                      ? "text-brand-500"
                      : "text-content-muted"
                  )}
                />
              </div>
              <span className="text-sm font-medium text-content-primary">
                {t.name}
              </span>
              <span className="text-xs text-content-muted">
                {t.desc}
              </span>
              {theme === t.value && (
                <div className="h-5 w-5 rounded-full bg-brand-500 flex items-center justify-center">
                  <Check className="h-3 w-3 text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* 通知设置 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <Bell className="h-5 w-5 text-amber-500" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              通知
            </h2>
            <p className="text-sm text-content-muted">
              管理您的通知偏好
            </p>
          </div>
        </div>
        <div className="space-y-4">
          <label className="flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-surface-border/50 cursor-pointer hover:bg-surface/80 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
                <Mail className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-content-primary">
                  邮件通知
                </p>
                <p className="text-xs text-content-muted">
                  接收产品更新和重要通知
                </p>
              </div>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
                className="sr-only peer"
              />
              <div className={cn(
                "w-11 h-6 rounded-full transition-colors",
                emailNotifications ? "bg-brand-500" : "bg-surface-border"
              )}>
                <div className={cn(
                  "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform",
                  emailNotifications && "translate-x-5"
                )} />
              </div>
            </div>
          </label>
          
          <label className="flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-surface-border/50 cursor-pointer hover:bg-surface/80 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
                <Mail className="h-5 w-5 text-accent-secondary" />
              </div>
              <div>
                <p className="text-sm font-medium text-content-primary">
                  营销邮件
                </p>
                <p className="text-xs text-content-muted">
                  接收促销和优惠信息
                </p>
              </div>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={marketingEmails}
                onChange={(e) => setMarketingEmails(e.target.checked)}
                className="sr-only peer"
              />
              <div className={cn(
                "w-11 h-6 rounded-full transition-colors",
                marketingEmails ? "bg-brand-500" : "bg-surface-border"
              )}>
                <div className={cn(
                  "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform",
                  marketingEmails && "translate-x-5"
                )} />
              </div>
            </div>
          </label>
        </div>
      </Card>
    </div>
  );
}
