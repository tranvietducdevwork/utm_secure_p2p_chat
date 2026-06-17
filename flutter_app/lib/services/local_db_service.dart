import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

import '../models/message.dart';

class LocalDbService {
  Database? _db;

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'secure_p2p_chat.db');
    return openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peer_username TEXT NOT NULL,
            content TEXT NOT NULL,
            is_mine INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            encrypted INTEGER NOT NULL DEFAULT 1
          )
        ''');
        await db.execute('''
          CREATE TABLE conversations (
            peer_username TEXT PRIMARY KEY,
            last_message TEXT,
            last_timestamp INTEGER
          )
        ''');
      },
    );
  }

  Future<void> saveMessage(ChatMessage message) async {
    final db = await database;
    await db.insert('messages', message.toMap()..remove('id'));
    await db.insert(
      'conversations',
      {
        'peer_username': message.peerUsername,
        'last_message': message.content,
        'last_timestamp': message.timestamp.millisecondsSinceEpoch,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<ChatMessage>> getMessages(String peerUsername) async {
    final db = await database;
    final rows = await db.query(
      'messages',
      where: 'peer_username = ?',
      whereArgs: [peerUsername],
      orderBy: 'timestamp ASC',
    );
    return rows.map(ChatMessage.fromMap).toList();
  }

  Future<List<Map<String, dynamic>>> getConversations() async {
    final db = await database;
    return db.query('conversations', orderBy: 'last_timestamp DESC');
  }
}
