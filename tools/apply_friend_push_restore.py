from pathlib import Path

G=Path('app/build.gradle');g=G.read_text();
if "firebase-messaging" not in g:g=g.replace("implementation 'com.google.firebase:firebase-firestore'","implementation 'com.google.firebase:firebase-firestore'\n    implementation 'com.google.firebase:firebase-messaging'")
G.write_text(g)

M=Path('app/src/main/AndroidManifest.xml');m=M.read_text()
if 'POST_NOTIFICATIONS' not in m:m=m.replace('<uses-permission android:name="android.permission.INTERNET" />','<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />')
if '.RoleplayMessagingService' not in m:m=m.replace('</application>','''<service android:name=".RoleplayMessagingService" android:exported="false"><intent-filter><action android:name="com.google.firebase.MESSAGING_EVENT" /></intent-filter></service>\n    </application>''')
M.write_text(m)

S=Path('app/src/main/java/com/hsnsn/actiontemplate/RoleplayMessagingService.java')
S.write_text(r'''package com.hsnsn.actiontemplate;
import android.app.NotificationChannel;import android.app.NotificationManager;import android.os.Build;import androidx.annotation.NonNull;import com.google.firebase.messaging.FirebaseMessagingService;import com.google.firebase.messaging.RemoteMessage;
public class RoleplayMessagingService extends FirebaseMessagingService{
 @Override public void onMessageReceived(@NonNull RemoteMessage msg){String title="طلب صداقة جديد",body="لديك طلب صداقة جديد";if(msg.getNotification()!=null){if(msg.getNotification().getTitle()!=null)title=msg.getNotification().getTitle();if(msg.getNotification().getBody()!=null)body=msg.getNotification().getBody();}NotificationManager nm=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);String ch="social_push";if(Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(new NotificationChannel(ch,"طلبات الصداقة",NotificationManager.IMPORTANCE_HIGH));android.app.Notification.Builder b=Build.VERSION.SDK_INT>=26?new android.app.Notification.Builder(this,ch):new android.app.Notification.Builder(this);b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle(title).setContentText(body).setAutoCancel(true);nm.notify((int)(System.currentTimeMillis()&0x7fffffff),b.build());}
 @Override public void onNewToken(@NonNull String token){super.onNewToken(token);com.google.firebase.auth.FirebaseUser u=com.google.firebase.auth.FirebaseAuth.getInstance().getCurrentUser();if(u!=null)com.google.firebase.firestore.FirebaseFirestore.getInstance().collection("users").document(u.getUid()).update("fcmToken",token);}
}''')

A=Path('app/src/main/java/com/hsnsn/actiontemplate/MainActivity.java');a=A.read_text()
anchor='        webView.loadUrl("file:///android_asset/index.html");'
if 'FirebaseMessaging.getInstance().getToken()' not in a:a=a.replace(anchor,'''        com.google.firebase.messaging.FirebaseMessaging.getInstance().getToken().addOnSuccessListener(token->{FirebaseUser u=currentUser();if(u!=null){ensureFirestore();firestore.collection("users").document(u.getUid()).set(java.util.Collections.singletonMap("fcmToken",token),com.google.firebase.firestore.SetOptions.merge());}});\n        webView.loadUrl("file:///android_asset/index.html");''')
A.write_text(a)
print('Restored FCM receiving and token registration for background friend-request push')