from datetime import datetime, timedelta
from vocaboost.database.db import db

class Progress(db.Model):
    """Model for tracking learning progress with spaced repetition"""
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    
    # Spaced repetition data
    memory_level = db.Column(db.Integer, default=0)  # 0-5 levels (0 = new, 5 = mastered)
    last_reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    next_review_at = db.Column(db.DateTime, default=datetime.utcnow)
    review_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Progress word_id={self.word_id} level={self.memory_level}>'
    
    @staticmethod
    def create_for_word(word_id):
        """Create initial progress for a word"""
        progress = Progress.query.filter_by(word_id=word_id).first()
        if not progress:
            progress = Progress(
                word_id=word_id,
                memory_level=0,
                next_review_at=datetime.utcnow()  # Due immediately
            )
            db.session.add(progress)
            db.session.commit()
        return progress
    
    def update_review(self, recalled_correctly):
        """Update after a review session"""
        self.review_count += 1
        self.last_reviewed_at = datetime.utcnow()
        
        # Update memory level based on recall success
        if recalled_correctly:
            if self.memory_level < 5:
                self.memory_level += 1
        else:
            # Reset to level 1 on failure
            self.memory_level = 1
            
        # Calculate next review date based on memory level
        interval_days = self.get_interval_days()
        self.next_review_at = datetime.utcnow() + timedelta(days=interval_days)
        
        db.session.commit()
        return self
    
    def get_interval_days(self):
        """Get interval days based on memory level"""
        intervals = {
            0: 0,     # New word - review immediately
            1: 1,     # Level 1 - review after 1 day
            2: 3,     # Level 2 - review after 3 days
            3: 7,     # Level 3 - review after 1 week
            4: 14,    # Level 4 - review after 2 weeks
            5: 30     # Level 5 - review after 1 month
        }
        return intervals.get(self.memory_level, 1)
    
    @staticmethod
    def get_due_words(limit=20):
        """Get words due for review"""
        now = datetime.utcnow()
        return Progress.query.filter(
            Progress.next_review_at <= now
        ).order_by(Progress.next_review_at).limit(limit).all()