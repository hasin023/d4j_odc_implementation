# Defects4J ODC Classification Report: Mockito-9

- Version: `9b`
- Work directory: `C:\d4j_work\postfix\Mockito_9b`
- Generated: `2026-07-25T14:48:40+00:00`

## Failure Summary
- `org.mockitousage.constructor.CreatingMocksWithConstructorTest::abstractMethodStubbed`: org.mockito.exceptions.base.MockitoException:
- `org.mockitousage.constructor.CreatingMocksWithConstructorTest::testCallsRealInterfaceMethod`: org.mockito.exceptions.base.MockitoException:
- `org.mockitousage.constructor.CreatingMocksWithConstructorTest::abstractMethodReturnsDefault`: org.mockito.exceptions.base.MockitoException:

## Suspicious Frames
- `$java.util.List$$EnhancerByMockitoWithCGLIB$$991aef83.get` at `at $java.util.List$$EnhancerByMockitoWithCGLIB$$991aef83.get(<generated>)`

## ODC Result
- **Evidence Mode**: ⚠️ Post-fix (with buggy->fixed diff)
- ODC Type: `improper handling of abstract methods in real method delegation`
- Family: `None`
- Target: `Design/Code`
- Confidence: `1.0`
- Needs Human Review: `False`

The bug occurs when a spy attempts to call a real method that internally invokes an abstract method. The original implementation of 'CallsRealMethods' blindly attempted to invoke the real method via reflection, which fails for abstract methods because they lack a concrete implementation. The fix introduces a check to see if the method being invoked is abstract; if it is, it delegates to the globally configured default answer instead of attempting to call the non-existent real implementation.
