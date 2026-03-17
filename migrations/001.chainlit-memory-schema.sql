CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'step_type') THEN
        CREATE TYPE step_type AS ENUM ('assistant_message', 'user_message', 'run', 'tool', 'llm');
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'feedback_value') THEN
        CREATE TYPE feedback_value AS ENUM ('like', 'dislike');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS "User" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "identifier" TEXT NOT NULL,
    "metadata" JSONB NOT NULL DEFAULT '{}'::JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS "User_identifier_key" ON "User" ("identifier");

CREATE TABLE IF NOT EXISTS "Thread" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" TEXT,
    "userId" TEXT,
    "userIdentifier" TEXT,
    "tags" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "metadata" JSONB NOT NULL DEFAULT '{}'::JSONB
);

ALTER TABLE "Thread"
    ADD COLUMN IF NOT EXISTS "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

UPDATE "Thread"
SET "updatedAt" = COALESCE("updatedAt", "createdAt", CURRENT_TIMESTAMP);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'Thread' AND constraint_name = 'Thread_userId_fkey'
    ) THEN
        ALTER TABLE "Thread"
            ADD CONSTRAINT "Thread_userId_fkey"
            FOREIGN KEY ("userId") REFERENCES "User"("id")
            ON DELETE SET NULL ON UPDATE CASCADE;
    END IF;
END$$;

CREATE INDEX IF NOT EXISTS "Thread_userId_idx" ON "Thread" ("userId");
CREATE INDEX IF NOT EXISTS "Thread_userIdentifier_idx" ON "Thread" ("userIdentifier");

CREATE TABLE IF NOT EXISTS "Step" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "name" TEXT,
    "type" TEXT NOT NULL,
    "threadId" TEXT,
    "parentId" TEXT,
    "streaming" BOOLEAN NOT NULL DEFAULT FALSE,
    "waitForAnswer" BOOLEAN,
    "isError" BOOLEAN,
    "metadata" JSONB NOT NULL DEFAULT '{}'::JSONB,
    "tags" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "input" TEXT,
    "output" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "startTime" TIMESTAMP(3),
    "endTime" TIMESTAMP(3),
    "generation" JSONB,
    "showInput" TEXT,
    "language" TEXT,
    "indent" INTEGER NOT NULL DEFAULT 0,
    "defaultOpen" BOOLEAN,
    "disableFeedback" BOOLEAN
);

ALTER TABLE "Step"
    ADD COLUMN IF NOT EXISTS "startTime" TIMESTAMP(3);

ALTER TABLE "Step"
    ADD COLUMN IF NOT EXISTS "endTime" TIMESTAMP(3);

ALTER TABLE "Step"
    ALTER COLUMN "streaming" SET DEFAULT FALSE;

UPDATE "Step"
SET "streaming" = FALSE
WHERE "streaming" IS NULL;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'Step' AND column_name = 'start'
    ) THEN
        EXECUTE 'UPDATE "Step" SET "startTime" = COALESCE("startTime", "start")';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'Step' AND column_name = 'end'
    ) THEN
        EXECUTE 'UPDATE "Step" SET "endTime" = COALESCE("endTime", "end")';
    END IF;
END$$;

ALTER TABLE "Step"
    ALTER COLUMN "name" DROP NOT NULL;

ALTER TABLE "Step"
    ALTER COLUMN "threadId" DROP NOT NULL;

ALTER TABLE "Step"
    ALTER COLUMN "type" TYPE TEXT USING "type"::TEXT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'Step' AND constraint_name = 'Step_threadId_fkey'
    ) THEN
        ALTER TABLE "Step"
            ADD CONSTRAINT "Step_threadId_fkey"
            FOREIGN KEY ("threadId") REFERENCES "Thread"("id")
            ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'Step' AND constraint_name = 'Step_parentId_fkey'
    ) THEN
        ALTER TABLE "Step"
            ADD CONSTRAINT "Step_parentId_fkey"
            FOREIGN KEY ("parentId") REFERENCES "Step"("id")
            ON DELETE SET NULL ON UPDATE CASCADE;
    END IF;
END$$;

CREATE INDEX IF NOT EXISTS "Step_threadId_idx" ON "Step" ("threadId");
CREATE INDEX IF NOT EXISTS "Step_parentId_idx" ON "Step" ("parentId");
CREATE INDEX IF NOT EXISTS "Step_createdAt_idx" ON "Step" ("createdAt");

CREATE TABLE IF NOT EXISTS "Element" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "threadId" TEXT,
    "type" TEXT NOT NULL,
    "url" TEXT,
    "chainlitKey" TEXT,
    "name" TEXT NOT NULL,
    "display" TEXT NOT NULL,
    "objectKey" TEXT,
    "size" TEXT,
    "page" INTEGER,
    "language" TEXT,
    "forId" TEXT,
    "mime" TEXT,
    "props" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'Element' AND constraint_name = 'Element_threadId_fkey'
    ) THEN
        ALTER TABLE "Element"
            ADD CONSTRAINT "Element_threadId_fkey"
            FOREIGN KEY ("threadId") REFERENCES "Thread"("id")
            ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'Element' AND constraint_name = 'Element_forId_fkey'
    ) THEN
        ALTER TABLE "Element"
            ADD CONSTRAINT "Element_forId_fkey"
            FOREIGN KEY ("forId") REFERENCES "Step"("id")
            ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END$$;

CREATE INDEX IF NOT EXISTS "Element_threadId_idx" ON "Element" ("threadId");
CREATE INDEX IF NOT EXISTS "Element_forId_idx" ON "Element" ("forId");

CREATE TABLE IF NOT EXISTS "Feedback" (
    "id" TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    "forId" TEXT NOT NULL,
    "value" feedback_value NOT NULL,
    "comment" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'Feedback' AND constraint_name = 'Feedback_forId_fkey'
    ) THEN
        ALTER TABLE "Feedback"
            ADD CONSTRAINT "Feedback_forId_fkey"
            FOREIGN KEY ("forId") REFERENCES "Step"("id")
            ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END$$;

CREATE UNIQUE INDEX IF NOT EXISTS "Feedback_forId_key" ON "Feedback" ("forId");
CREATE INDEX IF NOT EXISTS "Feedback_createdAt_idx" ON "Feedback" ("createdAt");
