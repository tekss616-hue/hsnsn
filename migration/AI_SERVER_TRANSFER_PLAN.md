# AI / Server transfer bundle

هذه الحزمة مرجع للنقل فقط ولا تدخل في بناء التطبيق الحالي.

## ننقل للمستودع الجديد

- `server/package.json`
- `server/.env.example`
- `server/src/admin-config.js`
- `server/src/secret-store.js`
- `server/src/nader-preview.js`
- `server/src/providers/openai-provider.js`

## نأخذ من `server/src/server.js` فقط

- تهيئة Firebase Admin.
- التحقق من Firebase ID Token (`requireUser`).
- صلاحية الإدارة (`requireAdmin`).
- `/api/health`.
- `/api/admin/ai/status`.
- `/api/admin/ai/key`.
- `/api/admin/ai/test`.
- `/api/admin/nader/session`.
- `/api/admin/nader/chat`.

## لا ننقل إلى الأساس الجديد

- `CaseEngine`.
- مجلد `server/cases`.
- `server/src/brain/case-engine.js`.
- `server/src/brain/game-master.js`.
- منطق التحقيق/القضية/الأدوار القديم.
- مسارات `/api/session`, `/api/my-role`, `/api/round-state`, `/api/game-master/feed`, `/api/chat`, `/api/accuse`, `/api/contradiction`, `/api/finalize`.
- مسارات إشعارات الأصدقاء من السيرفر القديم؛ نبني نظام السوشال الجديد لاحقًا بعد تثبيت الفكرة.

## نقاط يجب تعديلها بعد تحديد فكرة اللعبة

- `nader-preview.js` يحتوي حاليًا على سياق «مباراة اجتماعية/مختبر الشخصية»؛ نحفظ شخصية نادر وذاكرة الجلسة لكن نعيد كتابة السياق ليناسب الفكرة الجديدة.
- `openai-provider.js` ما زال يحتوي عبارات تحقيق وقضية؛ نحفظ طبقة الاتصال بـ OpenAI فقط ونكتب Prompt Builder جديد من الصفر.
- لا يتم نقل أي API key حقيقي إلى GitHub. المفاتيح تبقى Secrets/Environment فقط.

## العناصر المحفوظة

- شخصية نادر الأساسية وسلوكه.
- جلسات نادر وذاكرة المحادثة القصيرة.
- OpenAI Responses API integration.
- تشفير مفتاح OpenAI بـ AES-256-GCM.
- Firebase Admin authentication.
- حماية مسارات الإدارة بحساب الإدارة.
- إعدادات النموذج والمهلة والمنفذ عبر Environment variables.

الخطوة التالية: بعد إنشاء المستودع الجديد وإرسال اسمه، تُنقل هذه الأجزاء إليه كـ server مستقل نظيف، ثم نحدد فكرة اللعبة بالكامل قبل بناء واجهة أو عالم أو سوشال جديد.